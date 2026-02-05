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
        
    def execute(self, query: str, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        finally:
            self.release(conn)

    def release(self, conn):
        self.pool.release(conn)

    def close(self):
        self.pool.destroy()
        
    def get_connection(self):
        return self.pool.get_conn()
    
if __name__ == "__main__":
    db = Database()
    result = db.execute("SELECT 1")
    print(result)