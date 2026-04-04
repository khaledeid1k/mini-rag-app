from signal import signal

from fastapi import APIRouter , Depends,UploadFile,status
from fastapi.responses import JSONResponse 
from helpers.config import get_settings,Settings
from controllers import DataController, ProjectController ,ProcessController
import aiofiles
from models import ResponseStatus
import logging
from routes.schemes.data import BaseRequest

logger = logging.getLogger("uvicorn.error")
 
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
    file_path , file_id = data_controller.  generate_unique_filePath(original_filename=file.filename, profile_id=project_id)


    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(appsettings.FILE_DEFAULT_CHUNK_SIZE):  
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST) 
    return JSONResponse(content={
        "signal": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
        "file_id": file_id,
         
    })  

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, request: BaseRequest):
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    chunks = process_controller.process_file_content(file_content=file_content, 
                                                     file_id=file_id,
                                                       chunk_size=chunk_size,
                                                         overlap_size=overlap_size)  


    if chunks is  None :
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseStatus.FILE_PROCESSING_FAILED.value}) 
    return JSONResponse(content={
        "signal": ResponseStatus.FILE_PROCESSING_SUCCESS.value,
        "chunks": [chunk.dict() for chunk in chunks]
    })
    