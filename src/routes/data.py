from fastapi import FastAPI, APIRouter , Depends,UploadFile,status
from fastapi.responses import JSONResponse 
from helpers.config import get_settings,Settings
from controllers import DataController

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],

)

@data_router.post("/upload/{project_id}")

async def upload_file(project_id: str, file: UploadFile, appsettings : Settings=Depends(get_settings)):
    is_valid , message = DataController().validate_upload_file(file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": message})  
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": message})