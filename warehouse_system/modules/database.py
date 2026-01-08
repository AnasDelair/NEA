from pymysqlpool.pool import Pool
from dotenv import load_dotenv
from os import environ as env

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
        
    def query(self, query: string)

    def release(self, conn):
        self.pool.release(conn)

    def close(self):
        self.pool.destroy()
        
    def _get_conn(self):
        return self.pool.get_conn()


db = Database()