from .BaseController import BaseController
from models.db_schemes import Project , DataChunk
from typing import List, Dict
from stores.llm.LLMEnums import DocumentType


class NLPController(BaseController):
    def __init__(self,app,generation_client,embedding_client,vector_db_client):
        super().__init__(app)
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.vector_db_client = vector_db_client


    
    def create_collection_name(self,project_id:str):
        return f"project_{project_id}_collection".strip()
    

    def reset_vector_db_collection(self,project: Project):
       collection_name = self.create_collection_name(project_id=project.project_id)
       return self.vector_db_client.delete_collection(collection_name=collection_name)
    

    def get_vector_db_collection_info(self,project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vector_db_client.get_collection_info(collection_name=collection_name)
    

    def index_into_vector_db(self,project: Project, chunks: List[DataChunk],chunk_ids: List[int], do_reset: bool = False):
        
        # step 1 : get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step 2 : mange item
        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [{"chunk_order": chunk.chunk_order, "chunk_asset_id": chunk.chunk_asset_id} for chunk in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentType.DOCUMENT.value)
            for text in texts
        ]

        # step 3 : create collection if not exists
        self.vector_db_client.create_collection(
            collection_name=collection_name,
              embedding_size=self.embedding_client.embedding_size,
                do_reset=do_reset)
        
        # step 4 : insert data into collection

        self.vector_db_client.insert_many(
            collection_name=collection_name, 
            texts=texts,
              vectors=vectors,
                metadata=metadata,
                record_ids=chunk_ids)
        
        return True 