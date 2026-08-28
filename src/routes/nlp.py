from fastapi import APIRouter, Request , FastAPI , status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Dict, Any      
from routes.schemes.nlp import PushRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunckModel
from controllers.NLPController import NLPController
from models.enums.ResponseEnums import ResponseStatus
import logging



logger = logging.getLogger('uvicorn.error')



nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

 
@nlp_router.post("/index/push{project_id}}")
async def index_project(request: Request, project_id: str,push_request: PushRequest):


    project_model =await ProjectModel.create_instance(db_client=request.app.db_client)

    chunk_model = await ChunckModel.create_instance(db_client=request.app.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"message": f"Project with id {project_id} not found."}),
        )
    
    nlp_controller = NLPController(
        vector_db_client =request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client
    
                                   )



    has_records = True

    page_no = 1

    inserted_items_count = 0
    idx=0

    while has_records:

        page_chunks = await chunk_model.get_project_chuncks(project_id=project._id,page=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = await nlp_controller.index_into_vector_db(project=project,chunks=page_chunks,do_reset=push_request.do_reset,
                                                                chunk_ids=chunk_ids
                                                                )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                   "signal": ResponseStatus.INSERT_INTO_VECTOR_DB_FAILED.value, 
                },
            )
        inserted_items_count += len(page_chunks)


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        },
    )