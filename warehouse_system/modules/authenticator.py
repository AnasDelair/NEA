from database import Database
from hash_algorithm import Hash


class AuthService:
    def __init__(self, db: Database):
        self.db = db
        self.hash = Hash()

        self.query = "SELECT * FROM `login_details` WHERE user_id = 1"
        self.stored_password = self.db.execute(self.query)
        print(self.stored_password)

        def authenticate(self, username: str, password: str) -> bool:
            if not self.stored_password:
                success = self.reconcile()
                if not success:
                    print("password from database is invalid or not retrieved")
                    return False

                salt, password_hash = self.hash.hash_password(password)

                return self.hash.verify_password(password, ))

        def reconcile(self) -> bool:
            self.stored_password = self.db.execute(self.query)

            if not self.stored_password:
                return False

            return True
