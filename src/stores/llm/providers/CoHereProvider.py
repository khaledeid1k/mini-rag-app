import logging
import cohere
from ..LLMInterface import LLMInterface
from ..LLMEnums import CohereEnums, DocumentType, OpenAIEnums

class CohereProvider(LLMInterface):
    def __init__(self, api_key: str,default_input_max_chars: int = 1000,
                 default_output_max_tokens: int = 1000,
                    default_temperature: float = 0.1
                 ):
        self.api_key = api_key
        self.default_input_max_chars = default_input_max_chars
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generate_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)


        self.logger = logging.getLogger(__name__)

    def process_text(self, text: str):
        if len(text) > self.default_input_max_chars:
            logging.warning(f"Input text exceeds the maximum character limit of {self.default_input_max_chars}. It will be truncated.")
            return text[:self.default_input_max_chars].split()
        return text


    def set_generate_model(self, modeil_id: str) :
        self.generate_model_id = modeil_id 

    
    def set_embedding_model(self, model_id: str,embedding_size: int) :
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str,chat_history: list=[],max_output_tokens: int=None,
                        temperature: float=None) :  
            if self.client is None:
                logging.error("Cohere client is not initialized.")
                return None
        
            if self.generate_model_id is None:
                logging.error("Generate model ID is not set.")
                return None
            
            max_output_tokens = max_output_tokens or self.default_output_max_tokens
            temperature = temperature if temperature is not None else self.default_temperature
            
            response = self.client.chat(
            model=self.generate_model_id,
            chat_history=chat_history,
            messages= self.process_text(prompt), 
            max_tokens=max_output_tokens or self.default_output_max_tokens,
            temperature=temperature
            )
            
            if not response or not response.text:
                logging.error("No response received from Cohere API.")
                return None
            return response.text.strip()
            

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "text": self.process_text(prompt)}
    

    def embed_text(self, text: str, document_type: str = None):
        if self.client is None:
            logging.error("Cohere client is not initialized.")
            return None
        
        if self.embedding_model_id is None:
            logging.error("Embedding model ID is not set.")
            return None
        
        input_type = CohereEnums.DOCUMENT.value  
        if document_type == DocumentType.QUERY.value:
            input_type = CohereEnums.QUERY.value

        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"],
        )
        if not response or not response.embeddings or len(response.embeddings) == 0:
            logging.error("No embeddings returned from Cohere API.")
            return None
        return response.embeddings.float[0]