from fastapi import APIRouter, Request , FastAPI , status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Dict, Any      
from routes.schemes.nlp import PushRequest, SearchRequest
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

 
@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str,push_request: PushRequest):


    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)

    chunk_model = await ChunckModel.create_instance(db_client=request.app.state.db_client)

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

        page_chunks = await chunk_model.get_project_chuncks(project_id=project.id,page=page_no)

        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunk_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        should_reset_collection = bool(push_request.do_reset) and inserted_items_count == 0
        is_inserted = nlp_controller.index_into_vector_db(project=project,chunks=page_chunks,do_reset=should_reset_collection,
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


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)

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

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.VECTOR_DB_COLLECTION_RETRIEVE_SUCCESS.value,
            "collection_info": collection_info
        },
    )

@nlp_router.post("/index/search/{project_id}")
async def search_project_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse( 
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"message": f"Project with id {project_id} not found."}),
        )
    
    nlp_controller = NLPController(
        vector_db_client =request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
    
                                   )

    try:
        search_results = nlp_controller.search_vector_db_collection(
            project=project,
            query=search_request.query,
            limit=search_request.limit
        )
    except Exception as e:
        logger.error(f"Error during vector search: {e}")
        search_results = None

    if search_results is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseStatus.SEARCH_VECTOR_DB_COLLECTION_FAILED.value,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.SEARCH_VECTOR_DB_COLLECTION_SUCCESS.value,
            "search_results": [result.dict() for result in search_results]
        },
    )


@nlp_router.post("/index/answer/{project_id}")
async def answer_project_query(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model =await ProjectModel.create_instance(db_client=request.app.state.db_client)

    project= await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse( 
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder({"message": f"Project with id {project_id} not found."}),
        )
    
    nlp_controller = NLPController(
        vector_db_client =request.app.vector_db_client,
        embedding_client = request.app.embedding_client,
        generation_client = request.app.generation_client,
        template_parser = request.app.template_parser
                                   )

    answer , full_prompt , chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.query,
        limit=search_request.limit
    )
    if answer is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseStatus.ANSWER_RAG_QUESTION_FAILED.value,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseStatus.ANSWER_RAG_QUESTION_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        },
    ) 