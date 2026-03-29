import os
from controllers.BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus
from .ProjectController import ProjectController
import re


class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_upload_file(self, file:UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_EXTENSIONS:
            return False , ResponseStatus.FILE_TYPE_NOT_ALLOWED.value
        if file.size > self.settings.FILE_MAX_SIZE:
            return False , ResponseStatus.FILE_SIZE_EXCEEDS_LIMIT.value 
        

        return True , ResponseStatus.FILE_VALID.value
    
    def generate_unique_filename(self, original_filename: str,profile_id:str):
        random_key = self.generate_random_string()
        prject_path = ProjectController().get_project_path(project_id=profile_id)
        clean_filename = self.clean_filename(original_filename=original_filename)
        new_file_path = os.path.join(prject_path, f"{random_key}_{clean_filename}")
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(prject_path, f"{random_key}_{clean_filename}")

        return new_file_path

    def clean_filename(self, original_filename: str):
        # Remove any characters that are not alphanumeric, dots, underscores, or hyphens
        cleaned_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', original_filename)
        self.clean_filename = cleaned_filename.replace(' ', '_')  
        return cleaned_filename