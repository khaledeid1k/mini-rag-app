from fastapi import FastAPI, APIRouter , Depends
from helpers.config import get_settings,Settings
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],

)

@base_router.get("/")

async def welocome(appsettings : Settings=Depends(get_settings)):
    app_name = appsettings.APP_NAME
    app_version = appsettings.APP_VERSION
    return {"app_name": app_name, "app_version": app_version}