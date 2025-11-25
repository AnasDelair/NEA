from mysql.connector import pooling as pool
from dotenv import load_dotenv
from os import environ as env

load_dotenv()

class Database:
    def __init__(self):
        self.pool = pool.MySQLConnectionPool(
            pool_name="database",
            pool_size=5,
            pool_reset_session=True,
            host=env.get("DATABASE_HOST"),
            user=env.get("DATABASE_USER"),
            password=env.get("DATABASE_PASS"),
            database=env.get("DATABASE")
        )
        print(self.pool.get_connection())