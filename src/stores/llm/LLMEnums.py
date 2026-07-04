from enum import Enum


class LLMProvider(Enum):
    OPENAI = "OpenAI"
    AZURE_OPENAI = "Azure OpenAI"
    ANTHROPIC = "Anthropic"
    GOOGLE_PALM = "Google PaLM"
    COHERE = "Cohere"



class OpenAIEnums(Enum):
    SYSTEM = "system"
    USER = "user"   
    ASSISTANT = "assistant"


class CohereEnums(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
