from modules.database import Database

class InventoryService:
    def __init__(self, db: Database):
        self.db = db
        self.IMAGE_BASE = "https://a1cdp.com/themes/A1catering/images/prod_img/Rectangle/big_image/"

    def fetch_inventory(self, filter_type: str = "all") -> list:  # all, low, none
        base_query = """
        SELECT
            p.product_id,
            p.product_code,
            p.stock_code,
            p.description,
            p.capacity,
            COALESCE(SUM(pc.quantity),0) AS total_stock,
            COUNT(DISTINCT pc.pallet_id) AS pallet_count
        FROM products p
        LEFT JOIN pallet_contents pc
            ON p.product_id = pc.product_id
        GROUP BY p.product_id
        """

        if filter_type == "low":
            base_query += " HAVING total_stock < 100"
        elif filter_type == "none":
            base_query += " HAVING total_stock = 0"

        rows = self.db.query(base_query)

        for row in rows:
            if row.get("capacity") is not None:
                row["capacity"] = f"{row['capacity']} ml"

        return rows if rows else []

    def search_products(self, query: str):
        sql = """
        SELECT
            p.product_id,
            p.product_code,
            p.stock_code,
            p.description,
            p.capacity,
            COALESCE(SUM(pc.quantity),0) AS total_stock,
            COUNT(DISTINCT pc.pallet_id) AS pallet_count
        FROM products p
        LEFT JOIN pallet_contents pc
            ON p.product_id = pc.product_id
        WHERE
            p.product_code LIKE %s
            OR p.stock_code LIKE %s
            OR p.description LIKE %s
        GROUP BY p.product_id
        LIMIT 25
        """

        search = f"%{query}%"
        rows = self.db.query(sql, (search, search, search))

        for row in rows:
            if row.get("capacity") is not None:
                row["capacity"] = f"{row['capacity']} ml"

        return rows if rows else []

    def fetch_product(self, product_id: int):
        sql = """
        SELECT
            p.product_id,
            p.product_code,
            p.stock_code,
            p.description,
            p.dimensions,
            p.capacity,
            p.material,
            p.units_per_case,
            p.external_product_id,
            p.price_per_unit,
            p.cost_per_unit,
            p.image_key,
            COALESCE(SUM(pc.quantity),0) AS total_stock,
            COUNT(DISTINCT pc.pallet_id) AS pallet_count
        FROM products p
        LEFT JOIN pallet_contents pc
            ON p.product_id = pc.product_id
        WHERE p.product_id = %s
        GROUP BY p.product_id
        """

        rows = self.db.query(sql, (product_id,))
        if not rows:
            return None

        product = rows[0]

        if product.get("capacity") is not None:
            product["capacity"] = f"{product['capacity']} ml"

        if product.get("image_key"):
            product["image_url"] = f"{self.IMAGE_BASE}{product['image_key']}.jpg"
        else:
            product["image_url"] = None

        return product

    def fetch_product_pallets(self, product_id: int) -> list:
        """Return all pallets containing this product with their location and current quantity."""
        sql = """
        SELECT
            pa.pallet_id,
            pa.location_id,
            pa.date_stored,
            pc.quantity
        FROM pallets pa
        JOIN pallet_contents pc
            ON pa.pallet_id = pc.pallet_id
        WHERE pc.product_id = %s
          AND pc.quantity > 0
        ORDER BY pa.pallet_id ASC
        """
        rows = self.db.query(sql, (product_id,))
        return rows if rows else []

    def add_pallet(self, product_id: int, pallet_quantities: list) -> bool:
        num_pallets = len(pallet_quantities)

        locations = self.db.query(
            "SELECT location_id FROM locations ORDER BY location_id ASC"
        )

        free_locations = []

        for loc in locations:
            pallet = self.db.query_one(
                "SELECT pallet_id FROM pallets WHERE location_id=%s",
                (loc["location_id"],)
            )
            if not pallet:
                free_locations.append(loc["location_id"])
            if len(free_locations) >= num_pallets:
                break

        if len(free_locations) < num_pallets:
            return False

        for loc_id, qty in zip(free_locations, pallet_quantities):
            pallet_id = self.db.insert(
                "INSERT INTO pallets (location_id, date_stored) VALUES (%s, NOW())",
                (loc_id,)
            )
            self.db.execute(
                "INSERT INTO pallet_contents (pallet_id, product_id, quantity) VALUES (%s,%s,%s)",
                (pallet_id, product_id, qty)
            )

        return True

    def remove_stock(self, product_id: int, pallet_updates: list) -> bool:
        """
        pallet_updates: [{"pallet_id": int, "quantity": int}, ...]
        quantity is the amount to REMOVE from each pallet.
        """
        if not pallet_updates:
            return False

        for update in pallet_updates:
            pallet_id = update.get("pallet_id")
            qty = update.get("quantity", 0)
            if qty <= 0:
                continue

            res = self.db.query(
                "SELECT quantity FROM pallet_contents WHERE pallet_id=%s AND product_id=%s",
                (pallet_id, product_id)
            )
            if not res:
                continue

            current_qty = res[0]["quantity"]
            new_qty = max(current_qty - qty, 0)

            self.db.execute(
                "UPDATE pallet_contents SET quantity=%s WHERE pallet_id=%s AND product_id=%s",
                (new_qty, pallet_id, product_id)
            )

        return True


if __name__ == "__main__":
    db = Database()
    inventory_service = InventoryService(db)
    print(inventory_service.fetch_inventory())