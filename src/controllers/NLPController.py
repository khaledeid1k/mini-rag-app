from .BaseController import BaseController
from models.db_schemes import Project , DataChunk
from typing import List, Dict
from stores.llm.LLMEnums import DocumentType
import json


class NLPController(BaseController):
    def __init__(self,generation_client,embedding_client,vector_db_client,template_parser):
        super().__init__()
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.vector_db_client = vector_db_client
        self.template_parser = template_parser


    
    def create_collection_name(self,project_id:str):
        return f"project_{project_id}_collection".strip()
    

    def reset_vector_db_collection(self,project: Project):
       collection_name = self.create_collection_name(project_id=project.project_id)
       return self.vector_db_client.delete_collection(collection_name=collection_name)
    

    def get_vector_db_collection_info(self,project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info= self.vector_db_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )

    def index_into_vector_db(self,project: Project, chunks: List[DataChunk],chunk_ids: List[int], do_reset: bool = False):
        
        # step 1 : get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step 2 : mange item
        texts = [chunk.chunk_text for chunk in chunks]
        metadata = [
            {
                "chunk_order": chunk.chunk_order,
                "chunk_asset_id": str(chunk.chunk_asset_id) if chunk.chunk_asset_id else None,
            }
            for chunk in chunks
        ]
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

        is_inserted = self.vector_db_client.insert_many(
            collection_name=collection_name, 
            texts=texts,
              vectors=vectors,
                metadata=metadata,
                record_ids=chunk_ids)
        
        return is_inserted 


    def search_vector_db_collection(self,project: Project, query: str, limit: int = 5):
        collection_name = self.create_collection_name(project_id=project.project_id)
        query_vector = self.embedding_client.embed_text(text=query, document_type=DocumentType.QUERY.value)
        if query_vector is None or len(query_vector) == 0 :
            raise ValueError("Failed to generate embedding for the query.")
        
        search_results = self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        if search_results is None:
            return None
        return search_results

    def answer_rag_question(self,project: Project, query: str, limit: int = 10):
        search_results = self.search_vector_db_collection(project=project, query=query, limit=limit)

        if search_results is None or len(search_results) == 0: 
            raise ValueError("Failed to retrieve search results from the vector database.")
        
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(search_results)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history

