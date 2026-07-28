from pathlib import Path
import psycopg
from loguru import logger

from app.rag.loader import DocumentLoader
from app.rag.cleaner import DocumentCleaner
from app.rag.chunker import DocumentChunker
from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus
from app.config.settings import settings


def _pg_url() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def _ensure_columns() -> None:
    """Add chunk_index, page_number, needs_reindex to langchain_pg_embedding if missing."""
    with psycopg.connect(_pg_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE langchain_pg_embedding
                    ADD COLUMN IF NOT EXISTS chunk_index   INTEGER,
                    ADD COLUMN IF NOT EXISTS page_number   INTEGER,
                    ADD COLUMN IF NOT EXISTS needs_reindex BOOLEAN NOT NULL DEFAULT FALSE
            """)
        conn.commit()


def _sync_chunk_metadata() -> None:
    """Promote chunk_index and page_number from cmetadata JSONB into typed columns."""
    with psycopg.connect(_pg_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE langchain_pg_embedding
                SET
                    chunk_index = (cmetadata->>'chunk_index')::int,
                    page_number = (cmetadata->>'page_number')::int
                WHERE
                    chunk_index IS NULL
                    AND cmetadata ? 'chunk_index'
            """)
        conn.commit()


class Pipeline:

    def __init__(self):

        self.loader = DocumentLoader()
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker()

    # ----------------------------
    # Single File
    # ----------------------------

    def ingest(self, filepath: str):

        logger.info(f"Loading {filepath}")

        documents = self.loader.load(filepath)

        documents = self.cleaner.clean(documents)

        chunks = self.chunker.chunk(documents)

        logger.info(f"Adding {len(chunks)} chunks")

        vector_store.add_documents(chunks)
        bm25_corpus.add(chunks)
        _ensure_columns()
        _sync_chunk_metadata()

        return len(chunks)

    # ----------------------------
    # Entire Folder
    # ----------------------------

    def ingest_directory(self, folder: str):

        folder = Path(folder)

        total_files = 0
        total_chunks = 0

        for file in folder.rglob("*.md"):

            logger.info(f"Ingesting {file.name}")

            count = self.ingest(str(file))

            total_files += 1
            total_chunks += count

        logger.success(
            f"Indexed {total_files} files ({total_chunks} chunks)"
        )

        return total_files, total_chunks


try:
    _ensure_columns()
except Exception:
    pass  # DB may not be reachable at import time; ingest() will retry

pipeline = Pipeline()