from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne, UpdateOne, DeleteOne


class ChunckModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNKS_NAME.value]


    @classmethod 
    async def create_instance(cls,db_client:object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance   

    async def init_collection(self):   
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNKS_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnum.COLLECTION_CHUNKS_NAME.value)
        # Ensure indexes exist even for pre-existing collections.
        for index in DataChunk.get_indexes():
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_chunck(self,chunck:DataChunk):

        result = await self.collection.insert_one(chunck.dict(by_alias=True,exclude_unset=True))
        
        chunck._id = result.inserted_id

        return chunck
    
    async def get_chuncks_by_file_id(self,chunck_id:str):

        cursor = await self.collection.find_one({"_id": ObjectId(chunck_id)})  

        if cursor is None:
            return None
        
        
        return DataChunk(**cursor)
    


    async def insert_multiple_chuncks(self,chuncks:list,batch_size:int=100):

        for i in range(0 , len(chuncks) , batch_size):
            batch = chuncks[i:i+batch_size]


        operations = [
            InsertOne(chunck.dict(by_alias=True,exclude_unset=True))
            for chunck in batch]

        result = await self.collection.bulk_write(operations)

        return len(chuncks)
    


    async def delete_chuncks_by_project_id(self,project_id:ObjectId):

        result = await self.collection.delete_many({"chunk_project_id ": project_id})
        return result.deleted_count