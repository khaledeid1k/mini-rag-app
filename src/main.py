from fastapi import FastAPI
from routes import base,data
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from stores.llm.LLMProvidersFactory import LLMProividersFactory

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGO_DB_NAME]

    llm_providers_factory = LLMProividersFactory(settings)


    #generation client
    app.generation_client = llm_providers_factory.create_provider(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generate_model(settings.GENERATION_MODEL_ID)

    #embedding client
    app.embedding_client = llm_providers_factory.create_provider(provider=settings.EMBEDDING_BACK)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,settings.EMBEDDING_MODEL_EMBEDDING_SIZE)


@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)    