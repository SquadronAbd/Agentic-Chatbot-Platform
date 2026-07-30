import logging
from pathlib import Path
from typing import Callable

import httpx

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

    def _notify(self, callback_url: str | None, internal_key: str | None, status: str) -> None:
        if not callback_url:
            return
        try:
            httpx.post(
                callback_url,
                json={"status": status},
                headers={"X-Internal-Key": internal_key or ""},
                timeout=5,
            )
        except Exception as exc:
            logger.warning(f"Stage callback failed ({status}): {exc}")

    def ingest(
        self,
        file_path: str | Path,
        document_id: str | None = None,
        callback_url: str | None = None,
        internal_key: str | None = None,
    ) -> dict:

        file_path = Path(file_path)

        logger.info(f"Starting ingestion of {file_path.name}")

        notify = lambda s: self._notify(callback_url, internal_key, s)

        chunk_count = pipeline.ingest(str(file_path), on_stage=notify)

        logger.info(f"Ingestion complete ({chunk_count} chunks)")

        return {
            "success": True,
            "filename": file_path.name,
            "chunks": chunk_count,
        }
