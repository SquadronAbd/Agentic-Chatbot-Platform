import json
import uuid
from datetime import datetime, timedelta
from urllib import error, request

from airflow.decorators import dag, task

CHATBOT_DB_URL = (
    "postgresql://postgres:apppass@host.docker.internal:5434/chatbot_db"
)
BACKEND_API_URL = "http://host.docker.internal:8000/api/v1"
INTERNAL_API_KEY = "change-me-internal-key"

default_args = {
    "owner": "backend_team",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def _post_internal(path: str, payload: dict) -> dict:
    """Call a backend internal maintenance endpoint."""
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{BACKEND_API_URL}{path}",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Internal-Api-Key": INTERNAL_API_KEY,
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Backend API error {exc.code}: {detail}") from exc


@dag(
    dag_id="dag_document_health",
    default_args=default_args,
    description=(
        "Maintenance pipeline: detect stale/orphaned chunks, request re-indexing, "
        "verify vector deletion, sync metadata, and record a health summary"
    ),
    schedule=None,
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["maintenance", "documents", "rag"],
)
def dag_document_health():

    @task
    def scan_chunks_needing_reindex() -> list[str]:
        """Find chunks missing embeddings or explicitly marked for re-indexing."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            SELECT id::text
            FROM document_chunks
            WHERE embedding_id IS NULL OR needs_reindex = TRUE
        """)
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        chunk_ids = [row[0] for row in rows]
        print(f"Found {len(chunk_ids)} chunks needing re-index")
        return chunk_ids

    @task
    def request_embedding_regeneration(chunk_ids: list[str]) -> dict:
        """Ask the backend to forward re-index work to the AI/RAG service."""
        if not chunk_ids:
            print("No chunks to re-index.")
            return {"requested": 0, "chunk_ids": []}

        result = _post_internal(
            "/internal/documents/reindex-embeddings",
            {"chunk_ids": chunk_ids},
        )
        print(f"Re-index requested for {result.get('requested', 0)} chunks")
        return result

    @task
    def scan_orphaned_chunks() -> list[str]:
        """Find chunks whose parent document no longer exists."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            SELECT dc.id::text
            FROM document_chunks dc
            LEFT JOIN documents d ON d.id = dc.document_id
            WHERE d.id IS NULL
        """)
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        chunk_ids = [row[0] for row in rows]
        print(f"Found {len(chunk_ids)} orphaned chunks")
        return chunk_ids

    @task
    def verify_vectors_removed(chunk_ids: list[str]) -> list[str]:
        """Confirm orphaned chunk vectors are gone from the vector store."""
        if not chunk_ids:
            print("No orphaned chunks to verify.")
            return []

        result = _post_internal(
            "/internal/documents/verify-vector-deletion",
            {"chunk_ids": chunk_ids},
        )
        verified = result.get("verified", [])
        pending = result.get("pending", [])
        print(f"Verified {len(verified)} chunks; {len(pending)} still pending")
        return verified

    @task
    def delete_orphaned_chunks(verified_chunk_ids: list[str]) -> int:
        """Delete orphaned chunk rows only after vector deletion is confirmed."""
        if not verified_chunk_ids:
            print("No verified orphaned chunks to delete.")
            return 0

        from sqlalchemy import bindparam, create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        stmt = text(
            "DELETE FROM document_chunks WHERE id IN :chunk_ids"
        ).bindparams(bindparam("chunk_ids", expanding=True))
        with engine.begin() as conn:
            result = conn.execute(stmt, {"chunk_ids": verified_chunk_ids})
        deleted = result.rowcount
        print(f"Deleted {deleted} orphaned chunks")
        return deleted

    @task
    def verify_ready_documents() -> list[str]:
        """Find ready documents with no chunks or chunks missing embeddings."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            SELECT d.id::text
            FROM documents d
            LEFT JOIN document_chunks dc ON dc.document_id = d.id
            WHERE d.status = 'ready'
            GROUP BY d.id
            HAVING COUNT(dc.id) = 0
                OR BOOL_OR(dc.embedding_id IS NULL)
        """)
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        document_ids = [row[0] for row in rows]
        print(f"Found {len(document_ids)} inconsistent ready documents")
        return document_ids

    @task
    def update_document_metadata() -> int:
        """Refresh documents.chunk_count from actual chunk counts."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            UPDATE documents d
            SET chunk_count = sub.cnt
            FROM (
                SELECT d2.id, COUNT(dc.id) AS cnt
                FROM documents d2
                LEFT JOIN document_chunks dc ON dc.document_id = d2.id
                GROUP BY d2.id
            ) sub
            WHERE d.id = sub.id
              AND d.chunk_count IS DISTINCT FROM sub.cnt
        """)
        with engine.begin() as conn:
            result = conn.execute(query)

        updated = result.rowcount
        print(f"Updated chunk_count on {updated} documents")
        return updated

    @task
    def flag_inconsistent_records(document_ids: list[str]) -> int:
        """Mark invalid ready documents as inconsistent."""
        if not document_ids:
            print("No inconsistent documents to flag.")
            return 0

        from sqlalchemy import bindparam, create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        stmt = text(
            "UPDATE documents SET status = 'inconsistent' WHERE id IN :document_ids"
        ).bindparams(bindparam("document_ids", expanding=True))
        with engine.begin() as conn:
            result = conn.execute(stmt, {"document_ids": document_ids})
        flagged = result.rowcount
        print(f"Flagged {flagged} documents as inconsistent")
        return flagged

    @task
    def record_maintenance_summary(
        reindex_result: dict,
        orphans_found: list[str],
        orphans_deleted: int,
        metadata_updated: int,
        inconsistent_flagged: int,
        ds=None,
    ):
        """Persist a summary row for this maintenance run."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO document_health_runs (
                        id,
                        run_date,
                        reindex_requested,
                        orphans_found,
                        orphans_deleted,
                        inconsistent_flagged,
                        metadata_updated,
                        errors,
                        created_at
                    )
                    VALUES (
                        :id,
                        :run_date,
                        :reindex_requested,
                        :orphans_found,
                        :orphans_deleted,
                        :inconsistent_flagged,
                        :metadata_updated,
                        NULL,
                        NOW()
                    )
                """),
                {
                    "id": uuid.uuid4(),
                    "run_date": ds,
                    "reindex_requested": int(reindex_result.get("requested", 0)),
                    "orphans_found": len(orphans_found),
                    "orphans_deleted": orphans_deleted,
                    "inconsistent_flagged": inconsistent_flagged,
                    "metadata_updated": metadata_updated,
                },
            )
        print("Recorded document health run summary")

    reindex_ids = scan_chunks_needing_reindex()
    reindex_result = request_embedding_regeneration(reindex_ids)

    orphan_ids = scan_orphaned_chunks()
    verified_ids = verify_vectors_removed(orphan_ids)
    deleted_count = delete_orphaned_chunks(verified_ids)

    inconsistent_ids = verify_ready_documents()
    metadata_count = update_document_metadata()
    flagged_count = flag_inconsistent_records(inconsistent_ids)

    record_maintenance_summary(
        reindex_result,
        orphan_ids,
        deleted_count,
        metadata_count,
        flagged_count,
    )


dag_document_health()
