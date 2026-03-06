from modules.database import Database
from modules.authenticator import AuthService
from modules.inventory import InventoryService

class Services:
    def __init__(self):
        self.db = Database()

        self.auth = AuthService(self.db)
        self.inventory = InventoryService(self.db)

    def close(self):
        self.db.close()
        
Services = Services()
