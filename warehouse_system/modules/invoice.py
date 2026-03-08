from modules.database import Database


class InvoiceService:
    def __init__(self, db: Database):
        self.db = db

    def fetch_customers_dropdown(self) -> list:
        """All customers formatted for a dropdown."""
        sql = """
        SELECT c.customer_id, c.customer_type, cd.name
        FROM customers c
        JOIN customer_details cd ON c.customer_id = cd.customer_id
        ORDER BY c.customer_type ASC, cd.name ASC
        """
        return self.db.query(sql) or []

    def fetch_customer_list(self) -> list:
        """Full customer list for the customers tab."""
        sql = """
        SELECT
            c.customer_id,
            c.customer_type,
            cd.name,
            cd.address,
            cd.contact_number,
            COUNT(i.invoice_id) AS total_invoices,
            COALESCE(SUM(CASE WHEN i.status IN ('open','past_due') THEN i.amount ELSE 0 END), 0) AS outstanding
        FROM customers c
        JOIN customer_details cd ON c.customer_id = cd.customer_id
        LEFT JOIN invoices i ON c.customer_id = i.customer_id
        GROUP BY c.customer_id
        ORDER BY cd.name ASC
        """
        return self.db.query(sql) or []

    def add_customer(self, name: str, address: str, contact_number: str) -> int:
        customer_id = self.db.insert(
            "INSERT INTO customers (customer_type) VALUES ('company')"
        )
        self.db.execute(
            "INSERT INTO customer_details (customer_id, name, address, contact_number) VALUES (%s, %s, %s, %s)",
            (customer_id, name, address, contact_number)
        )
        return customer_id

    # ── Invoices ─────────────────────────────────────────────────────────────

    def _mark_overdue(self):
        """Flip any open invoices whose due_date has passed to past_due."""
        self.db.execute(
            "UPDATE invoices SET status = 'past_due' WHERE status = 'open' AND due_date < CURDATE()"
        )

    def fetch_invoices(self, filter_type: str = "all") -> list:
        self._mark_overdue()

        sql = """
        SELECT
            i.invoice_id,
            i.invoice_date,
            i.due_date,
            i.status,
            i.amount,
            cd.name AS customer_name
        FROM invoices i
        JOIN customer_details cd ON i.customer_id = cd.customer_id
        """

        params = ()
        if filter_type == "drafts":
            sql += " WHERE i.status = 'draft'"
        elif filter_type == "open":
            sql += " WHERE i.status = 'open'"
        elif filter_type == "past-due":
            sql += " WHERE i.status = 'past_due'"
        elif filter_type == "paid":
            sql += " WHERE i.status = 'paid'"

        sql += " ORDER BY i.invoice_date DESC"

        rows = self.db.query(sql, params if params else None) or []

        for row in rows:
            if row.get("invoice_date"):
                row["invoice_date"] = str(row["invoice_date"])
            if row.get("due_date"):
                row["due_date"] = str(row["due_date"])

        return rows

    def fetch_product_by_stock_code(self, stock_code: str) -> dict | None:
        sql = """
        SELECT p.product_id, p.product_code, p.stock_code, p.description, p.price_per_unit,
            COALESCE(SUM(pc.quantity), 0) AS total_stock
        FROM products p
        LEFT JOIN pallet_contents pc ON p.product_id = pc.product_id
        WHERE p.stock_code = %s
        GROUP BY p.product_id
        """
        return self.db.query_one(sql, (stock_code,))

    def create_invoice(self, customer_id: int, items: list, status: str, due_date: str) -> int | bool:
        """
        items: [{"product_id": int, "quantity": int, "price_each": float}, ...]
        Returns invoice_id on success, False if insufficient stock.
        """
        # Validate stock levels first
        for item in items:
            product_id = item["product_id"]
            qty_needed = item["quantity"]

            total = self.db.query_one(
                "SELECT COALESCE(SUM(quantity), 0) AS total FROM pallet_contents WHERE product_id = %s",
                (product_id,)
            )
            if not total or total["total"] < qty_needed:
                return False

        # Calculate total amount
        amount = sum(item["quantity"] * item["price_each"] for item in items)

        # Insert invoice
        invoice_id = self.db.insert(
            "INSERT INTO invoices (customer_id, invoice_date, due_date, status, amount) VALUES (%s, CURDATE(), %s, %s, %s)",
            (customer_id, due_date, status, amount)
        )

        # Insert line items
        for item in items:
            self.db.execute(
                "INSERT INTO invoice_items (invoice_id, product_id, quantity, price_each) VALUES (%s, %s, %s, %s)",
                (invoice_id, item["product_id"], item["quantity"], item["price_each"])
            )

        # Only deduct stock if not a draft
        if status != "draft":
            for item in items:
                self._deduct_stock(item["product_id"], item["quantity"])

        return invoice_id

    def _deduct_stock(self, product_id: int, qty_to_remove: int):
        """Remove qty from pallets starting from the lowest-quantity pallet first."""
        pallets = self.db.query(
            """
            SELECT pa.pallet_id, pc.quantity
            FROM pallets pa
            JOIN pallet_contents pc ON pa.pallet_id = pc.pallet_id
            WHERE pc.product_id = %s AND pc.quantity > 0
            ORDER BY pc.quantity ASC
            """,
            (product_id,)
        )

        remaining = qty_to_remove

        for pallet in pallets:
            if remaining <= 0:
                break

            pallet_id = pallet["pallet_id"]
            available = pallet["quantity"]
            take = min(available, remaining)
            new_qty = available - take
            remaining -= take

            if new_qty == 0:
                # Remove pallet_contents row and the pallet itself
                self.db.execute(
                    "DELETE FROM pallet_contents WHERE pallet_id = %s AND product_id = %s",
                    (pallet_id, product_id)
                )
                # Only delete pallet if it has no other contents
                other = self.db.query_one(
                    "SELECT 1 FROM pallet_contents WHERE pallet_id = %s LIMIT 1",
                    (pallet_id,)
                )
                if not other:
                    self.db.execute("DELETE FROM pallets WHERE pallet_id = %s", (pallet_id,))
            else:
                self.db.execute(
                    "UPDATE pallet_contents SET quantity = %s WHERE pallet_id = %s AND product_id = %s",
                    (new_qty, pallet_id, product_id)
                )

    def mark_paid(self, invoice_id: int) -> bool:
        affected = self.db.execute(
            "UPDATE invoices SET status = 'paid' WHERE invoice_id = %s AND status IN ('open', 'past_due')",
            (invoice_id,)
        )
        return affected > 0

    def delete_invoice(self, invoice_id: int) -> bool:
        """
        If invoice is a draft, restore stock before deleting.
        For open/past_due invoices stock was already deducted — just delete.
        """
        invoice = self.db.query_one(
            "SELECT status FROM invoices WHERE invoice_id = %s", (invoice_id,)
        )
        if not invoice:
            return False

        # Drafts never had stock removed, so no restoration needed.
        # Delete line items first (FK constraint), then invoice.
        self.db.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (invoice_id,))
        self.db.execute("DELETE FROM invoices WHERE invoice_id = %s", (invoice_id,))
        return True

    def save_draft_as_open(self, invoice_id: int) -> bool:
        """Promote a draft to open and deduct stock."""
        invoice = self.db.query_one(
            "SELECT status FROM invoices WHERE invoice_id = %s", (invoice_id,)
        )
        if not invoice or invoice["status"] != "draft":
            return False

        items = self.db.query(
            "SELECT product_id, quantity FROM invoice_items WHERE invoice_id = %s",
            (invoice_id,)
        )

        # Validate stock
        for item in items:
            total = self.db.query_one(
                "SELECT COALESCE(SUM(quantity), 0) AS total FROM pallet_contents WHERE product_id = %s",
                (item["product_id"],)
            )
            if not total or total["total"] < item["quantity"]:
                return False

        self.db.execute(
            "UPDATE invoices SET status = 'open' WHERE invoice_id = %s",
            (invoice_id,)
        )

        for item in items:
            self._deduct_stock(item["product_id"], item["quantity"])

        return True

    def search_invoices(self, query: str) -> list:
        sql = """
        SELECT
            i.invoice_id,
            i.invoice_date,
            i.due_date,
            i.status,
            i.amount,
            cd.name AS customer_name
        FROM invoices i
        JOIN customer_details cd ON i.customer_id = cd.customer_id
        WHERE cd.name LIKE %s
        ORDER BY i.invoice_date DESC
        LIMIT 25
        """
        search = f"%{query}%"
        rows = self.db.query(sql, (search,)) or []
        for row in rows:
            if row.get("invoice_date"):
                row["invoice_date"] = str(row["invoice_date"])
            if row.get("due_date"):
                row["due_date"] = str(row["due_date"])
        return rows


if __name__ == "__main__":
    db = Database()
    invoice_service = InvoiceService(db)