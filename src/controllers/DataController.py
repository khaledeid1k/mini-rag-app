
from controllers.BaseController import BaseController
from fastapi import UploadFile
from models import ResponseStatus


class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_upload_file(self, file:UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_EXTENSIONS:
            return False , ResponseStatus.FILE_TYPE_NOT_ALLOWED.value
        if file.size > self.settings.FILE_MAX_SIZE:
            return False , ResponseStatus.FILE_SIZE_EXCEEDS_LIMIT.value 
        

        return True , ResponseStatus.FILE_VALID.value