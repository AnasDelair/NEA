import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from warehouse_system.modules.database import Database

# MAKE CAPACITY REMOVE ML ON JSON

def extract_image_key(image_url):
    if not image_url:
        return None
    return Path(image_url).stem

def extract_external_product_id(url):
    if not url:
        return None
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return int(qs["product_id"][0]) if "product_id" in qs else None

with open("warehouse_system/storage/products.json", "r", encoding="utf-8") as f:
    products = json.load(f)


db = Database()

insert_sql = """
INSERT INTO products (
    product_id,
    product_code,
    stock_code,
    description,
    dimensions,
    capacity,
    material,
    units_per_case,
    image_key,
    external_product_id
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    product_code = VALUES(product_code),
    stock_code = VALUES(stock_code),
    description = VALUES(description),
    dimensions = VALUES(dimensions),
    capacity = VALUES(capacity),
    material = VALUES(material),
    units_per_case = VALUES(units_per_case),
    image_key = VALUES(image_key),
    external_product_id = VALUES(external_product_id)
"""

conn = db.get_connection()
inserted = 0

try:
    with conn.cursor() as cursor:
        for p in products:
            cursor.execute(
                insert_sql,
                (
                    p.get("product_id"),
                    p.get("product_code"),
                    p.get("stock_code"),
                    p.get("description"),
                    p.get("dimensions"),
                    p.get("capacity"),
                    p.get("material"),
                    int(p["units_per_case"]) if p.get("units_per_case") else None,
                    extract_image_key(p.get("image_url")),
                    extract_external_product_id(p.get("url")),
                )
            )
            inserted += 1

    conn.commit()

finally:
    db.release(conn)

print(f"Upserted {inserted} products")
