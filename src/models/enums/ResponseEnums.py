from enum import Enum 


class ResponseStatus(Enum):
    FILE_TYPE_NOT_ALLOWED = "File type not allowed"
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds the maximum limit"
    FILE_VALID = "File is valid"
    FILE_UPLOAD_SUCCESS = "File uploaded successfully"
    FILE_UPLOAD_FAILED = "File upload failed" 
    FILE_PROCESSING_FAILED = "File processing failed"
    FILE_PROCESSING_SUCCESS = "File processed successfully"
    NO_FILES_TO_PROCESS = "No files to process"
    FILE_NOT_FOUND = "File not found"
    INSERT_INTO_VECTOR_DB_FAILED = "Failed to insert into vector database"
    INSERT_INTO_VECTOR_DB_SUCCESS = "Successfully inserted into vector database"