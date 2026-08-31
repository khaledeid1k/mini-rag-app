from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import QdrantClient , models
import logging
from typing import List, Dict, Any
from models.db_schemes.data_chunk import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self,dp_path:str,distance_method:str):
        self.client = None
        self.distance_method = None
        self.dp_path = dp_path 


        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT


        self.logger = logging.getLogger(__name__)



    
    def connect(self):
        self.client = QdrantClient(path=self.dp_path)
        self.logger.info("Connected to QdrantDB")

    
    def disconnect(self):
        self.client=None


    def is_collection_exists(self, collection_name: str) -> bool:
        try:
            return self.client.collection_exists(collection_name) 
        except Exception as e:
            self.logger.error(f"Error checking collection existence: {e}")
            return False
        

    def list_all_collections(self) -> List:
        try:
            return self.client.get_collections()
        except Exception as e:
            self.logger.error(f"Error listing collections: {e}")
            return []
        
    
    def get_collection_info(self, collection_name: str) -> dict:
        try:
            return self.client.get_collection(collection_name)
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            return {}
        

    def delete_collection(self, collection_name: str):
        if self.is_collection_exists(collection_name):
            try:
                self.client.delete_collection(collection_name)
                self.logger.info(f"Collection {collection_name} deleted successfully.")
            except Exception as e:
                self.logger.error(f"Error deleting collection: {e}")


    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if self.is_collection_exists(collection_name):
            if do_reset:
                self.delete_collection(collection_name)
            else:
                self.logger.info(f"Collection {collection_name} already exists. Skipping creation.")
                return

        try:
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method)
            )
            self.logger.info(f"Collection {collection_name} created successfully.")
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")


    def insert_one(self, collection_name: str, text :str,vector:List,metadata:dict=None,record_id:str=None):
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist. Cannot insert data.")
            return
        
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, **(metadata or {})}
                    )
                ],
            )
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False
        

        return True 
    


    def insert_many(self, 
                    collection_name: str,
                      texts: List, 
                      vectors: List,
                      metadata:dict=None,
                      record_ids:List=None,
                      batch_size:int=50,):
        
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        
        for i in range(0, len(texts), batch_size):
            batch_end= min(i + batch_size, len(texts))
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]
 
            batch_records = [
               models.PointStruct(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], **(batch_metadata[x] or {})}
                )
                for x in range(len(batch_texts))
            ]
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch records: {e}")
                return False

        return True
    


    def search_by_vector(self, collection_name: str, query_vector: List, limit: int=5) :
        if not self.is_collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist. Cannot perform search.")
            return None
        
        try:
            if hasattr(self.client, "query_points"):
                search_result = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=limit
                )
                results = search_result.points if hasattr(search_result, "points") else search_result
                return [RetrievedDocument(**{
                    "text": result.payload.get("text", "") if result.payload else "",
                    "score": result.score
                })
                for result in results
                ]
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            if search_result is not None:
                return [RetrievedDocument(**{
                    "text": result.payload.get("text", "") if result.payload else "",
                    "score": result.score
                })
                for result in search_result
                ]
            else:
                self.logger.warning(f"No results found for the search in collection {collection_name}.")
                return []
        except Exception as e:
            self.logger.error(f"Error searching by vector: {e}")
            return None
