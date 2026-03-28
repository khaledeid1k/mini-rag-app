from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],

)

@base_router.get("/")

async def welocome():
    app_name = os.getenv("APP_NAME", "My FastAPI App")
    app_version = os.getenv("APP_VERSION", "1.0.0")
    return {"app_name": app_name, "app_version": app_version}