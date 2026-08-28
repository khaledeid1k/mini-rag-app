from fastapi import FastAPI
from routes import base,data, nlp
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from stores.llm.LLMProvidersFactory import LLMProividersFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGO_DB_NAME]

    llm_providers_factory = LLMProividersFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    #generation client
    app.generation_client = llm_providers_factory.create_provider(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generate_model(settings.GENERATION_MODEL_ID)

    #embedding client
    app.embedding_client = llm_providers_factory.create_provider(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,settings.EMBEDDING_MODEL_SIZE)


    #vector db client
    app.vector_db_client = vector_db_provider_factory.create_provider(provider_name=settings.VECTOR_DB_BACKEND)
    app.vector_db_client.connect()

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()
    app.vector_db_client.disconnect()

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)    