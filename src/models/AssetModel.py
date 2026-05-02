from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]

    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):   
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSETS_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnum.COLLECTION_ASSETS_NAME.value)
        # Ensure indexes exist even for pre-existing collections.
        for index in Asset.get_indexes():
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])    

    async def create_asset(self,asset:Asset):

        result = await self.collection.insert_one(asset.dict(by_alias=True,exclude_unset=True))  # Use by_alias to ensure _id is used instead of id, and exclude_unset to avoid inserting None fields
        
        asset.id = result.inserted_id

        return asset
    

    async def get_all_project_assets(self,asset_project_id:str):

        return self.collection.find(
            {"asset_project_id":ObjectId(asset_project_id) if isinstance(asset_project_id,str) else asset_project_id}
            
            ).to_list(length=None )