from enum import Enum 


class ResponseStatus(Enum):
    FILE_TYPE_NOT_ALLOWED = "File type not allowed"
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds the maximum limit"
    FILE_VALID = "File is valid"
    FILE_UPLOAD_SUCCESS = "File uploaded successfully"
    FILE_UPLOAD_FAILED = "File upload failed" 
    FILE_PROCESSING_FAILED = "File processing failed"
    FILE_PROCESSING_SUCCESS = "File processed successfully"