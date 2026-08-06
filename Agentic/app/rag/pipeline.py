import hashlib
from pathlib import Path
import psycopg
from loguru import logger

from app.rag.loader import DocumentLoader
from app.rag.cleaner import DocumentCleaner
from app.rag.chunker import DocumentChunker
from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus
from app.rag.metadata import MetadataExtractor
from app.rag.doc_store import remove_source
from app.config.settings import settings


def _pg_url() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def _file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _stored_hash(source: str, owner_id: str | None = None, document_id: str | None = None) -> str | None:
    """Return the content_hash stored for this source file, or None if not found."""
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT cmetadata->>'content_hash' FROM langchain_pg_embedding "
                    "WHERE cmetadata->>'source' = %s "
                    "AND (%s IS NULL OR cmetadata->>'owner_id' = %s) "
                    "AND (%s IS NULL OR cmetadata->>'document_id' = %s) LIMIT 1",
                    (source, owner_id, owner_id, document_id, document_id),
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as exc:
        logger.warning("Hash check failed for {}: {}", source, exc)
        return None


def _delete_by_source(source: str, owner_id: str | None = None, document_id: str | None = None) -> int:
    """Delete all pgvector chunks for a given source file. Returns deleted count."""
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'source' = %s "
                    "AND (%s IS NULL OR cmetadata->>'owner_id' = %s) "
                    "AND (%s IS NULL OR cmetadata->>'document_id' = %s)",
                    (source, owner_id, owner_id, document_id, document_id),
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


def _backend_pg_url() -> str | None:
    """Return the chatbot_db URL, or None if not configured."""
    url = settings.BACKEND_DB_URL
    if not url:
        return None
    return url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg://", "postgresql://")


def _write_chunks_to_backend_db(document_id: str, chunks: list) -> None:
    """
    Mirror ingested chunk metadata into chatbot_db.document_chunks so the
    document-health pipeline can verify consistency.

    Fetches embedding UUIDs from langchain_pg_embedding (financial_rag), then
    upserts rows into document_chunks (chatbot_db).  Silently skips if
    BACKEND_DB_URL is unset or either DB is unreachable.
    """
    backend_url = _backend_pg_url()
    if not backend_url or not document_id:
        return

    # --- fetch embedding UUIDs from the vector store DB ---
    embedding_map: dict[int, str] = {}  # chunk_index -> embedding UUID
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT uuid::text, (cmetadata->>'chunk_index')::int "
                    "FROM langchain_pg_embedding "
                    "WHERE cmetadata->>'document_id' = %s",
                    (document_id,),
                )
                for emb_uuid, chunk_idx in cur.fetchall():
                    if chunk_idx is not None:
                        embedding_map[chunk_idx] = emb_uuid
    except Exception as exc:
        logger.warning("Could not fetch embedding UUIDs for document {}: {}", document_id, exc)

    # --- upsert into chatbot_db.document_chunks ---
    try:
        with psycopg.connect(backend_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM document_chunks WHERE document_id = %s",
                    (document_id,),
                )
                for i, chunk in enumerate(chunks):
                    chunk_idx = chunk.metadata.get("chunk_index", i)
                    page_num = chunk.metadata.get("page_number")
                    emb_id = embedding_map.get(int(chunk_idx)) if chunk_idx is not None else None
                    cur.execute(
                        """
                        INSERT INTO document_chunks
                            (id, document_id, content, chunk_index, page_number, embedding_id, needs_reindex)
                        VALUES
                            (gen_random_uuid(), %s, %s, %s, %s, %s, FALSE)
                        """,
                        (document_id, chunk.page_content, chunk_idx, page_num, emb_id),
                    )
            conn.commit()
        logger.info(
            "Synced {} chunk(s) to chatbot_db.document_chunks for document {}",
            len(chunks), document_id,
        )
    except Exception as exc:
        logger.warning(
            "Could not write chunks to backend DB for document {}: {}", document_id, exc
        )


class Pipeline:

    def __init__(self):

        self.loader = DocumentLoader()
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker()

    # ----------------------------
    # Single File
    # ----------------------------

    def ingest(self, filepath: str, on_stage=None, *, owner_id: str | None = None,
               document_id: str | None = None, filename: str | None = None):

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
        stored = _stored_hash(source, owner_id, document_id)

        if stored == new_hash:
            logger.info("Skipping {} — content unchanged (hash match)", Path(filepath).name)
            return 0

        if stored is not None:
            deleted = _delete_by_source(source, owner_id, document_id)
            logger.info("File updated — deleted {} old chunks for {}", deleted, Path(filepath).name)
            if owner_id or document_id:
                bm25_corpus.remove_by_metadata(owner_id, document_id)
            else:
                bm25_corpus.remove_by_source(source)

        # ── ingestion ────────────────────────────────────────────────────────
        logger.info("ingestion parsing source={} owner_id={} document_id={}", source, owner_id, document_id)
        _notify("ingesting")
        documents = self.loader.load(filepath)
        logger.info("ingestion cleaning source={} documents={}", source, len(documents))
        documents = self.cleaner.clean(documents)

        _notify("chunking")
        chunks = self.chunker.chunk(documents)
        logger.info("ingestion chunking source={} chunks={}", source, len(chunks))
        chunks = MetadataExtractor.enrich(
            chunks, source, owner_id=owner_id, document_id=document_id,
            filename=filename, content_hash=new_hash,
        )

        logger.info("ingestion embedding source={} chunks={}", source, len(chunks))
        _notify("embedding")
        vector_store.add_documents(chunks)
        logger.info("ingestion vector insertion source={} chunks={}", source, len(chunks))
        bm25_corpus.add(chunks)
        _ensure_columns()
        _sync_chunk_metadata()

        if document_id:
            _write_chunks_to_backend_db(document_id, chunks)

        return len(chunks)

    def delete_document_chunks(self, owner_id: str, document_id_or_source: str) -> int:
        """Delete a document's vectors, BM25 entries, and Redis source mapping."""
        is_source = document_id_or_source.startswith("/")
        source = str(Path(document_id_or_source).resolve()) if is_source else None
        try:
            with psycopg.connect(_pg_url()) as conn:
                with conn.cursor() as cur:
                    if source:
                        cur.execute("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'owner_id' = %s AND cmetadata->>'source' = %s", (str(owner_id), source))
                    else:
                        cur.execute("DELETE FROM langchain_pg_embedding WHERE cmetadata->>'owner_id' = %s AND cmetadata->>'document_id' = %s", (str(owner_id), str(document_id_or_source)))
                    deleted = cur.rowcount
                conn.commit()
        except Exception as exc:
            logger.error("Failed document cleanup owner_id={} document={}: {}", owner_id, document_id_or_source, exc)
            raise
        if source:
            bm25_corpus.remove_by_source(source)
            remove_source(str(owner_id), source)
        else:
            bm25_corpus.remove_by_metadata(str(owner_id), str(document_id_or_source))
        logger.info("Deleted {} chunks for owner_id={} document={}", deleted, owner_id, document_id_or_source)
        return deleted

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
