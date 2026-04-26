from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum



class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]

    
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):   
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECTS_NAME.value not in all_collections:
            await self.db_client.create_collection(DataBaseEnum.COLLECTION_PROJECTS_NAME.value)
        # Ensure indexes exist even for pre-existing collections.
        for index in Project.get_indexes():
            await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])    

    async def create_project(self,project:Project):

        result = await self.collection.insert_one(project.dict(by_alias=True,exclude_unset=True))  # Use by_alias to ensure _id is used instead of id, and exclude_unset to avoid inserting None fields
        
        #project._id = result.inserted_id

        # Return a new Project instance with the inserted _id
        return Project(**{**project.dict(), "_id": result.inserted_id})
      
        #return project
    

    async def get_project_or_create_one(self,project_id:str):

        record = await self.collection.find_one({"project_id":project_id})

        if record is  None:
            project = Project(project_id=project_id)
            return await self.create_project(project=project)
    
        return Project(**record)
    

    async def get_all_projects(self,page:int=1,page_size:int=10):

        # count total documents for pagination
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size

        if total_documents % page_size > 0:
            total_pages += 1

        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)    

        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        
        return projects, total_pages