from mysql.connector import pooling as pool
from mysql.connector import connect
from dotenv import load_dotenv
from os import environ as env

load_dotenv()

class Database:
    def __init__(self):
        #self.pool = pool.MySQLConnectionPool(
        #    pool_name="database",
        #    pool_size=5,
        #    pool_reset_session=True,
        #    host=env.get("DATABASE_HOST"),
        #    user=env.get("DATABASE_USER"),
        #    password=env.get("DATABASE_PASS"),
        #    database=env.get("DATABASE")
        #)
        
        # print(self.pool.get_connection())

        context = connect(
            user="u381396247_adelair", 
            password="I&ac@aCp&0", 
            host="srv1475.hstgr.io", 
            port="3306", 
            database="u381396247_adelair"
            )
        
        print("connected")
        
        context.close()

if __name__ == "__main__":
    print("running")
    db = Database()