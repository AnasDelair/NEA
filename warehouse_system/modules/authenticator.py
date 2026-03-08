from modules.database import Database
from modules.hash_algorithm import Hash

class AuthService:

    def __init__(self, db: Database):
        self.db = db
        self.hash = Hash()

        self.query = "SELECT * FROM login_details WHERE user_id = 1"

        row = self.db.query_one(self.query)
        self.stored_data = self._deserialise(row) if row else None


    def authenticate(self, input_password: str) -> bool:

        if not self.stored_data:
            if not self._reconcile():
                return False

        return self.hash.verify_password(
            input_password,
            self.stored_data["salt"],
            self.stored_data["password_hash"]
        )


    def _reconcile(self) -> bool:

        row = self.db.query_one(self.query)

        if not row:
            print("password from database is invalid or not retrieved")
            return False

        self.stored_data = self._deserialise(row)
        return self.stored_data is not None


    def _deserialise(self, data: dict) -> dict:

        try:
            return {
                "user_id": int(data["user_id"]),
                "password_hash": int(data["password_hash"]),
                "salt": int(data["salt"])
            }
        except (KeyError, TypeError, ValueError):
            return None


if __name__ == "__main__":
    db = Database()
    auth_service = AuthService(db)

    print(auth_service.authenticate("admin"))