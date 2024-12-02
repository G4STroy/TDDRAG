import asyncio
import tracemalloc
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents.agent_manager import AgentManager
from middleware.telemetry import TelemetryMiddleware
import uvicorn
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from config.config import Config

agent_manager = AgentManager()

# Wrap the entire execution in a try-except block
try:
    async def initialize_agent_manager():
        try:
            await agent_manager.initialize()
            # Your FastAPI app setup and other initializations here
        except Exception as e:
            logger.error(f"Error initializing AgentManager: {str(e)}")

    async def cleanup_agent_manager():
        if 'agent_manager' in locals():
            await agent_manager.cleanup()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        await agent_manager.initialize()
        yield
        # Shutdown
        await agent_manager.cleanup()

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(TelemetryMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("FastAPI application configured")

    @app.post("/upload")
    async def upload_file(file: UploadFile = File(...)):
        logger.info(f"Received upload request for file: {file.filename}")
        try:
            content = await file.read()
            result = await agent_manager.ingestion_agent.upload_document(file.filename, content)
            if result:
                logger.info(f"File {file.filename} uploaded and indexed successfully")
                return {"success": True, "message": "File uploaded and indexed successfully"}
            else:
                logger.error(f"Failed to upload or index file {file.filename}")
                return {"success": False, "message": "Failed to upload or index file"}
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            logger.exception("Full traceback:")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/index")
    async def index_documents():
        logger.info("Received request to index documents")
        try:
            result = await agent_manager.indexing_agent.index_documents()
            logger.info("Documents indexed successfully")
            return {"success": result}
        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    class QueryRequest(BaseModel):
        query: str = Field(..., min_length=1, max_length=1000)
        search_type: str = Field(..., pattern="^(Vector|Hybrid)$")

    @app.post("/query")
    async def query_llm(request: QueryRequest):
        logger.info(f"Received query request: {request.query}, search type: {request.search_type}")
        try:
            search_results, llm_response = await agent_manager.langchain_agent.process_query(request.query, request.search_type)
            logger.info("Query processed successfully")
            return {"search_results": search_results, "llm_response": llm_response}
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/document_count")
    async def get_document_count():
        try:
            count = await agent_manager.indexing_agent.get_document_count()
            return {"count": count}
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            logger.exception("Full traceback:")
            raise HTTPException(status_code=500, detail="Internal server error")

    description="API for document ingestion, search, and question answering",
    @app.get("/list_documents")
    async def list_documents():
        logger.info("Received request to list documents")
        try:
            documents = await agent_manager.indexing_agent.list_documents()
            logger.info(f"Retrieved {len(documents)} documents")
            return {"documents": [doc.as_dict() for doc in documents]}
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return JSONResponse(status_code=500, content={"error": str(e)})

    from fastapi.openapi.utils import get_openapi

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="Document Search and QA API",
            version="1.0.0",
            description="API for document ingestion, search, and question answering",
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi

    @app.post("/delete_documents")
    async def delete_documents(request: dict):
        logger.info("Received request to delete documents")
        try:
            if request.get('deleteAll'):
                result = await agent_manager.indexing_agent.delete_all_documents()
            else:
                documents = request.get('documents', [])
                result = await agent_manager.indexing_agent.delete_documents(documents)
            
            if result:
                logger.info("Documents deleted successfully")
                return {"success": True, "message": "Documents deleted successfully"}
            else:
                logger.error("Failed to delete documents")
                return {"success": False, "message": "Failed to delete documents"}
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return {"success": False, "message": str(e)}

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up application")
        try:
            await agent_manager.initialize()
            logger.info("Application startup complete")
        except Exception as e:
            logger.error(f"Error during startup: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.agent_manager.cleanup()

    @app.get("/status")
    async def check_status():
        try:
            # Check connection to Azure services
            await agent_manager.indexing_agent.get_document_count()
            return {"status": "ok", "message": "All services are operational"}
        except Exception as e:
            logger.error(f"Service health check failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    if __name__ == "__main__":
        logger.info("Starting FastAPI application")
        uvicorn.run(app, host="0.0.0.0", port=8000)

except Exception as e:
    logger.critical(f"Unhandled exception occurred: {str(e)}")
    logger.critical(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

@app.get("/list_indexed_documents")
async def list_indexed_documents():
    try:
        documents = await agent_manager.indexing_agent.list_indexed_documents()
        logger.info(f"Retrieved {len(documents)} indexed documents")
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Error listing indexed documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))