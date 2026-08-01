import hashlib
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


def _file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _stored_hash(source: str) -> str | None:
    """Return the content_hash stored for this source file, or None if not found."""
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT cmetadata->>'content_hash' FROM langchain_pg_embedding "
                    "WHERE cmetadata->>'source' = %s LIMIT 1",
                    (source,),
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as exc:
        logger.warning("Hash check failed for {}: {}", source, exc)
        return None


def _delete_by_source(source: str) -> int:
    """Delete all pgvector chunks for a given source file. Returns deleted count."""
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'source' = %s",
                    (source,),
                )
                deleted = cur.rowcount
            conn.commit()
        return deleted
    except Exception as exc:
        logger.error("Failed to delete chunks for {}: {}", source, exc)
        return 0


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

    def ingest(self, filepath: str, on_stage=None):

        def _notify(stage: str):
            if on_stage:
                try:
                    on_stage(stage)
                except Exception:
                    pass

        # ── content-hash dedup ───────────────────────────────────────────────
        # Compute SHA-256 of the file and compare to the stored hash.
        # Skip entirely if unchanged; delete old chunks first if the file was updated.
        source = str(Path(filepath).resolve())
        new_hash = _file_sha256(filepath)
        stored = _stored_hash(source)

        if stored == new_hash:
            logger.info("Skipping {} — content unchanged (hash match)", Path(filepath).name)
            return 0

        if stored is not None:
            deleted = _delete_by_source(source)
            logger.info("File updated — deleted {} old chunks for {}", deleted, Path(filepath).name)
            bm25_corpus.remove_by_source(source)

        # ── ingestion ────────────────────────────────────────────────────────
        logger.info(f"Loading {filepath}")
        _notify("ingesting")
        documents = self.loader.load(filepath)
        documents = self.cleaner.clean(documents)

        _notify("chunking")
        chunks = self.chunker.chunk(documents)

        # Stamp the content hash into each chunk's metadata so we can retrieve it later
        for chunk in chunks:
            chunk.metadata["content_hash"] = new_hash

        logger.info(f"Adding {len(chunks)} chunks")
        _notify("embedding")
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