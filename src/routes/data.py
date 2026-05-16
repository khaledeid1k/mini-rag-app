from operator import index
from signal import signal

from fastapi import APIRouter , Depends,UploadFile,status , Request
from fastapi.responses import JSONResponse 
from helpers.config import get_settings,Settings
from controllers import DataController, ProjectController ,ProcessController
import aiofiles
from models import ResponseStatus
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunckModel
from models.AssetModel import AssetModel
import logging
from routes.schemes.data import BaseRequest
from models.db_schemes import DataChunk , Asset
import os

logger = logging.getLogger("uvicorn.error")
 
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],

)

@data_router.post("/upload/{project_id}")

async def upload_file(request: Request, project_id: str, file: UploadFile, appsettings : Settings=Depends(get_settings)):


    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

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
    #store asset into db
    asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)
    asset_resource = Asset(
        asset_id=file_id,
        asset_project_id=project.id,
        asset_type="file",
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
    )
    asset_recorde=   await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(content={
        "signal": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
        "file_id": str(asset_recorde.id),
    })  

@data_router.post("/process/{project_id}")
async def process_file(project_id: str, request: Request,base_request: BaseRequest):
    chunk_size = base_request.chunk_size
    overlap_size = base_request.overlap_size
    do_reset = base_request.do_reset


    project_model = await ProjectModel.create_instance(db_client=request.app.state.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    chunk_model = await ChunckModel.create_instance(db_client=request.app.state.db_client)
    
    if do_reset==True : 
         _ = await chunk_model.delete_chuncks_by_project_id(project_id=project.id)


    project_files_ids =[]
    asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)

    if base_request.file_id:
        asset_record = await asset_model.get_asset_record(asset_project_id=project.id, asset_name=base_request.file_id)
        if asset_record is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseStatus.FILE_NOT_FOUND.value})
        
        project_files_ids={
            asset_record.id: asset_record.asset_name
        }
    else:
        project_assets = await asset_model.get_all_project_assets(asset_project_id=project.id,asset_type="file")
        project_files_ids = {
         record.id: record.asset_name
            for record in project_assets
        }


    if len(project_files_ids)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseStatus.NO_FILES_TO_PROCESS.value})    
    process_controller = ProcessController(project_id=project_id)

    no_of_chunks_inserted = 0
    no_files = 0
    for asset_id ,  file_id in project_files_ids.items() :

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"File with id {file_id} not found in project {project_id}")
            continue
        if file_content is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseStatus.FILE_TYPE_NOT_ALLOWED.value})
        chunks = process_controller.process_file_content(file_content=file_content, 
                                                        file_id=file_id,
                                                        chunk_size=chunk_size,
                                                            overlap_size=overlap_size)  


        if chunks is  None :
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": ResponseStatus.FILE_PROCESSING_FAILED.value}) 
        

        file_chunks_records = [
            
            
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id

            )                    
                            
            for i, chunk in enumerate(chunks)
            ]        

        no_of_chunks_inserted = await chunk_model.insert_multiple_chuncks(chuncks=file_chunks_records)
        no_files += 1

    return JSONResponse(content={
        "signal": ResponseStatus.FILE_PROCESSING_SUCCESS.value,
        "file_id": file_id,
        "chunks_created": no_of_chunks_inserted,
        "files_processed": no_files,
    })
    