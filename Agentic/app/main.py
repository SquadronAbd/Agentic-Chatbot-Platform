import os
import shutil
from contextlib import asynccontextmanager
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, Form, UploadFile, File, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.utils.logger import logger
from app.config.settings import settings
from app.rag.rag_service import RAGService
from app.evaluation.evaluator import RAGEvaluator
from app.rag.pipeline import pipeline
from app.rag.bm25_corpus import bm25_corpus
from app.memory.session import session_manager
from app.tools.retriever_tool import RetrieverTool
from app.user_ingestion.upload_service import UploadService


@asynccontextmanager
async def lifespan(app: FastAPI):
    bm25_corpus.bootstrap(settings.DATABASE_URL, settings.COLLECTION_NAME)
    yield


app = FastAPI(
    title="Enterprise AI Assistant API",
    description="FastAPI Backend for Enterprise Multi-Agent RAG Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
retriever_tool = RetrieverTool()
rag_evaluator = RAGEvaluator()

# ----------------------------------------------------
# Pydantic Schemas
# ----------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(
    ...,
    json_schema_extra={
        "example": "session-123"
    }
)
    question: str = Field(
    ...,
    json_schema_extra={
        "example": "What is RAG?"
    }
)

class ChatResponse(BaseModel):
    success: bool
    session_id: str
    question: str
    answer: str
    summary: str = ""
    messages: int = 0
    documents_retrieved: int = 0
    sources: List[Dict[str, Any]] = []
    error: Optional[str] = None

class IngestDirectoryRequest(BaseModel):
    directory_path: str = Field(
        ..., json_schema_extra={
        "example":"documents"
        }
    )

class SearchRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example":"semantic search"})
    k: int = Field(default=3, ge=1, le=20)

class ClearMemoryRequest(BaseModel):
    session_id: str = Field(..., json_schema_extra={"example":"session-123"})

class EvaluateRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "What was the revenue in Q3?"})
    actual_output: str = Field(..., json_schema_extra={"example": "Revenue was $5.2B in Q3 2024."})
    retrieval_context: List[str] = Field(
        ..., json_schema_extra={"example": ["Q3 revenue reached $5.2B...", "..."]}
    )
    expected_output: Optional[str] = Field(
        default=None,
        json_schema_extra={"example": "Revenue in Q3 was $5.2 billion."},
    )
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)

# ----------------------------------------------------
# Endpoints
# ----------------------------------------------------

@app.get("/health", tags=["System"])
def health_check():
    """
    Health status check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Enterprise AI Assistant",
        "collection_name": settings.COLLECTION_NAME,
        "embedding_model": settings.EMBEDDING_MODEL,
    }

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Process user query via AgentManager and LangGraph workflow.
    The LangGraph pipeline is synchronous (LLM calls are blocking), so it
    runs in a thread-pool executor to avoid blocking the event loop.
    """
    import asyncio
    from functools import partial
    try:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(
            None,
            partial(rag_service.ask, session_id=request.session_id, question=request.question),
        )
        return res
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.post("/ingest", tags=["Ingestion"])
async def ingest_file(
    file: UploadFile = File(...),
    document_id: str = Form(None),
    callback_url: str = Form(None),
    internal_key: str = Form(None),
):
    """
    Upload and ingest a user document (PDF, TXT, MD)
    into the RAG knowledge base.
    """

    try:

        upload_dir = "documents/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(
            upload_dir,
            file.filename or "uploaded file",
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        upload_service = UploadService()

        result = upload_service.ingest(
            file_path,
            document_id=document_id,
            callback_url=callback_url,
            internal_key=internal_key,
        )

        return result

    except Exception as e:

        logger.error(
            f"Failed to ingest file {file.filename}: {e}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest file: {str(e)}",
        )

@app.post("/ingest-directory", tags=["Ingestion"])
def ingest_directory(request: IngestDirectoryRequest):
    """
    Ingest all markdown/pdf documents from a given directory path.
    """
    try:
        if not os.path.exists(request.directory_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Directory path '{request.directory_path}' not found.",
            )

        total_files, total_chunks = pipeline.ingest_directory(request.directory_path)

        return {
            "success": True,
            "directory": request.directory_path,
            "files_processed": total_files,
            "chunks_added": total_chunks,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting directory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.get("/sessions", tags=["Sessions"])
def list_sessions():
    """
    Retrieve all active session IDs.
    """
    sessions = session_manager.list_sessions()
    return {
        "success": True,
        "total_sessions": len(sessions),
        "sessions": sessions,
    }

@app.delete("/sessions/{session_id}", tags=["Sessions"])
def delete_session(session_id: str):
    """
    Delete a session and its conversation memory.
    """
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session deleted successfully.",
    }

@app.post("/clear-memory", tags=["Sessions"])
def clear_memory(request: ClearMemoryRequest):
    """
    Clear memory history for a specific session without deleting it.
    """
    cleared = session_manager.clear_session(request.session_id)
    return {
        "success": True,
        "session_id": request.session_id,
        "cleared": cleared,
    }

@app.get("/documents", tags=["Admin"])
def get_documents_info():
    """
    Get administrative information about vector store, documents, and system collection.
    """
    return {
        "success": True,
        "collection_name": settings.COLLECTION_NAME,
        "embedding_model": settings.EMBEDDING_MODEL,
        "database": "PostgreSQL (pgvector)",
        "active_sessions": session_manager.total_sessions(),
    }

@app.post("/search", tags=["Search"])
def search_documents(request: SearchRequest):
    """
    Perform standalone semantic document search.
    """
    try:
        res = retriever_tool.search(request.query)
        docs = res.get("documents", [])

        results = []
        for doc in docs[:request.k]:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": doc.metadata.get("score", None),
            })

        return {
            "success": True,
            "query": request.query,
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.post("/evaluate", tags=["Evaluation"])
async def evaluate_rag(request: EvaluateRequest):
    """
    Score a single RAG response with five DeepEval metrics using Groq as the LLM judge.

    Always-on metrics (no ground truth needed):
    - ContextualRelevancy  — are retrieved chunks relevant to the query?
    - AnswerRelevancy      — does the answer address the question?
    - Faithfulness         — is every claim grounded in retrieved context?

    Requires expected_output (ground truth):
    - ContextualPrecision  — are relevant chunks ranked above irrelevant ones?
    - ContextualRecall     — do chunks cover the expected answer?
    """
    import asyncio
    from functools import partial

    evaluator = RAGEvaluator(threshold=request.threshold)
    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            partial(
                evaluator.score,
                query=request.query,
                actual_output=request.actual_output,
                retrieval_context=request.retrieval_context,
                expected_output=request.expected_output,
            ),
        )
        overall_passed = all(
            v.get("passed") for v in results.values() if v.get("passed") is not None
        )
        return {
            "success": True,
            "overall_passed": overall_passed,
            "threshold": request.threshold,
            "metrics": results,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))