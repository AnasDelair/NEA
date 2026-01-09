from database import Database
from hash_algorithm import Hash

class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.hash = Hash()
        
    def authenticate(self, username: str, password: str) -> bool:
        query = "SELECT password FROM users WHERE username=%s"
        result = self.db.execute(query, (username,))
        if not result:
            return False
        stored_password = result[0]['password']
        return stored_password == password