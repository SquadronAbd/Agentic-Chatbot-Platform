import logging
from pathlib import Path

from app.rag.pipeline import pipeline
from app.user_ingestion.parser import DocumentParser

logger = logging.getLogger(__name__)


class UploadService:
    """
    Handles user-uploaded document ingestion.

    Flow:

    Uploaded File
            ↓
        DocumentParser
            ↓
        Existing RAG Pipeline
            ↓
        Cleaner
            ↓
        Chunker
            ↓
        Embeddings
            ↓
        Vector Store
            ↓
        BM25
    """

    def __init__(self):
        self.parser = DocumentParser()

    def ingest(self, file_path: str | Path) -> dict:

        file_path = Path(file_path)

        logger.info(
            f"Starting ingestion of {file_path.name}"
        )

        # Parse uploaded document
        documents = self.parser.parse(str(file_path))

        # Pass parsed documents into the existing pipeline
        chunk_count = pipeline.ingest_documents(
            documents
        )

        logger.info(
            f"Ingestion complete ({chunk_count} chunks)"
        )

        return {
            "success": True,
            "filename": file_path.name,
            "chunks": chunk_count,
        }