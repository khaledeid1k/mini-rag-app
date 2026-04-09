from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")  # maps MongoDB's _id
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value
    

    model_config = {
        "arbitrary_types_allowed": True,  # needed for ObjectId
        "populate_by_name": True,         # allows using 'id' OR '_id'
    }