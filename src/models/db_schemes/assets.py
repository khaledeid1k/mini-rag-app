from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import ASCENDING


class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")  # maps MongoDB's _id
    asset_id: str = Field(..., min_length=1)
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config : dict = Field(default=None)
    asset_pushed_at: datetime = Field(default=datetime.utcnow)


    model_config = {
        "arbitrary_types_allowed": True,  # needed for ObjectId
        "populate_by_name": True,         # allows using 'id' OR '_id'
    }



    @classmethod
    def get_indexes(cls):
        return [{
            
                "key": [("asset_project_id", ASCENDING)],
                "name": "asset_project_id_index_1",
                "unique": False 
        },
        {
            
                "key": [("asset_project_id", ASCENDING),
                        ("asset_name", ASCENDING)],
                "name": "asset_project_id_asset_name_index_1",
                "unique": True
        }
            ]