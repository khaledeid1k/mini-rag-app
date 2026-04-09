from fastapi import FastAPI
from routes import base,data
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.state.mongo_conn = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db_client = app.state.mongo_conn[settings.MONGO_DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)    