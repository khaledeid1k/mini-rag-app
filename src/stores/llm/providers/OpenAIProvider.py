import logging

from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str,api_url: str=None,default_input_max_chars: int = 1000,
                 default_output_max_tokens: int = 1000,
                    default_temperature: float = 0.1
                 ):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_chars = default_input_max_chars
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generate_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(api_key=self.api_key, api_url=self.api_url)


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
            logging.error("OpenAI client is not initialized.")
            return None
    
        if self.generate_model_id is None:
            logging.error("Generate model ID is not set.")
            return None
        
        max_output_tokens = max_output_tokens or self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(self.construct_prompt(prompt = prompt, role = OpenAIEnums.USER.value))
        
        response = self.client.chat.completions.create(
            model=self.generate_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            logging.error("No valid response returned from OpenAI.")
            return None
        return response.choices[0].message.content

    

    def embed_text(self, text: str,document_type: str=None) :
       if self.client is None:
            logging.error("OpenAI client is not initialized.")
       if self.embedding_model_id is None:
            logging.error("Embedding model ID is not set.")
       response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text)

       if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding :
            logging.error("No embedding data returned from OpenAI.")
            return None
       return response.data[0].embedding    
    

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self.process_text(prompt)}