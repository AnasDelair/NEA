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
            db=env["DATABASE"],
            autocommit=True
        )
        self.pool.init()

    def _get_conn(self):
        conn = self.pool.get_conn()
        try:
            conn.ping(reconnect=True)
        except Exception:
            # If ping itself fails, try to get a fresh connection
            self.pool.release(conn)
            conn = self.pool.get_conn()
            conn.ping(reconnect=True)
        return conn

    def _release(self, conn):
        self.pool.release(conn)

    # SELECT many rows
    def query(self, sql: str, params=None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            self._release(conn)

    # SELECT one row
    def query_one(self, sql: str, params=None):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    # INSERT returning id
    def insert(self, sql: str, params=None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.lastrowid
        finally:
            self._release(conn)

    def execute(self, sql: str, params=None):
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.rowcount
        finally:
            self._release(conn)

    def close(self):
        self.pool.destroy()