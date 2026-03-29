from signal import signal

from fastapi import FastAPI, APIRouter , Depends,UploadFile,status
from fastapi.responses import JSONResponse 
from helpers.config import get_settings,Settings
from controllers import DataController, ProjectController 
import aiofiles
import os
from models import ResponseStatus
 
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],

)

@data_router.post("/upload/{project_id}")

async def upload_file(project_id: str, file: UploadFile, appsettings : Settings=Depends(get_settings)):
    data_controller = DataController()
    is_valid , message = data_controller .validate_upload_file(file)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": message})  
    # else:
    #     return JSONResponse(status_code=status.HTTP_200_OK, content={"message": message})
    
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path = data_controller.  generate_unique_filename(original_filename=file.filename, profile_id=project_id)

    async with aiofiles.open(file_path, 'wb') as out_file:
        while chunk := await file.read(appsettings.FILE_DEFAULT_CHUNK_SIZE):  
            await out_file.write(chunk)

    return JSONResponse(content={
        "signal": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
         
    })  