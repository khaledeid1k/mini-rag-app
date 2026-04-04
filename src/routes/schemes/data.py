from pydantic import BaseModel
from typing import Optional

class BaseRequest(BaseModel):
    file_id: str
    chunk_size: Optional[int] = 200  # Default chunk size is 200 characters
    overlap_size: Optional[int] = 20  # Default overlap size is 20 characters
    do_reset: Optional[bool] = False  # Whether to reset the file pointer after reading