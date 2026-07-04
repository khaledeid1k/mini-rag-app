from helpers.config import get_settings,Settings
import os
import random
import string

class BaseController:
    def __init__(self):

        self.settings = get_settings()
        
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        
        self.files_dir = os.path.join(self.base_dir, "assets/files")

        self.database_dir = os.path.join(self.base_dir, "assets/database")

    def generate_random_string(self, length=12):
        letters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(letters,k=length))
    


    def get_database_path(self, database_name: str):
        self.database_path = os.path.join(self.database_dir, database_name)

        if not os.path.exists(self.database_path):
            os.makedirs(self.database_path)

        return self.database_path