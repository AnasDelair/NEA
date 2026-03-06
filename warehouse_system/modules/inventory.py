from modules.database import Database

class InventoryService:
    def __init__(self, db: Database):
        self.db = db
        IMAGE_BASE = "https://a1cdp.com/themes/A1catering/images/prod_img/Rectangle/big_image/"

    def fetch_inventory(self, filter_type: str = "all") -> list: # all, low, none
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

        rows = self.db.execute(base_query)
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

        return self.db.execute(sql, (search, search, search))
    
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

        rows = self.db.execute(sql, (product_id,))
        if not rows:
            return None

        product = rows[0]

        if product["image_key"]:
            product["image_url"] = f"{self.IMAGE_BASE}{product['image_key']}.jpg"
        else:
            product["image_url"] = None

        return product


if __name__ == "__main__":
    db = Database()
    inventory_service = InventoryService(db)

    print(inventory_service.fetch_inventory())