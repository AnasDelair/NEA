from pymysqlpool.pool import Pool
from dotenv import load_dotenv
from os import environ as env
import pymysql

load_dotenv()

class Database:
    def __init__(self):
        self.pool = Pool(
            host=env["DATABASE_HOST"],
            user=env["DATABASE_USER"],
            password=env["DATABASE_PASS"],
            db=env["DATABASE"]
        )
        self.pool.init()

    def execute(self, query: str, params=None):
        conn = self.pool.get_conn()
        try:
            conn.ping(reconnect=True)

            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)

                if query.strip().lower().startswith("select"):
                    return cursor.fetchall()

                conn.commit()
        finally:
            self.pool.release(conn)

    def close(self):
        self.pool.destroy()