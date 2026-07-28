"""
Maintenance operations against langchain_pg_embedding in pgvector.
Called by the backend DAG via POST /maintenance/reindex and /maintenance/verify-deletion.
"""
import psycopg
from app.config.settings import settings
from app.models.embeddings import embeddings
from app.utils.logger import logger


def _pg_url() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def reindex_chunks(chunk_ids: list[str]) -> list[str]:
    """
    Re-generate and update the embedding vector for each given chunk ID.
    Returns the list of chunk IDs that were successfully reindexed.
    """
    if not chunk_ids:
        return []

    reindexed: list[str] = []

    with psycopg.connect(_pg_url()) as conn:
        for chunk_id in chunk_ids:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT document FROM langchain_pg_embedding WHERE id = %s",
                    (chunk_id,),
                )
                row = cur.fetchone()
                if row is None:
                    logger.warning(f"[reindex] chunk {chunk_id} not found — skipping")
                    continue

                text = row[0]
                try:
                    vector = embeddings.embed_query(text)
                except Exception as e:
                    logger.error(f"[reindex] embedding failed for {chunk_id}: {e}")
                    continue

                cur.execute(
                    "UPDATE langchain_pg_embedding SET embedding = %s WHERE id = %s",
                    (vector, chunk_id),
                )
                reindexed.append(chunk_id)

        conn.commit()

    logger.info(f"[reindex] reindexed {len(reindexed)}/{len(chunk_ids)} chunks")
    return reindexed


def verify_deletion(chunk_ids: list[str], embedding_ids: list[str]) -> dict[str, list[str]]:
    """
    Check whether the given chunk IDs still exist in langchain_pg_embedding.
    Returns {"verified": [...], "pending": [...]}
      - verified: IDs confirmed gone from the DB
      - pending:  IDs still present in the DB
    """
    if not chunk_ids:
        return {"verified": [], "pending": []}

    verified: list[str] = []
    pending: list[str] = []

    with psycopg.connect(_pg_url()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM langchain_pg_embedding WHERE id = ANY(%s)",
                (chunk_ids,),
            )
            still_present = {str(row[0]) for row in cur.fetchall()}

    for chunk_id in chunk_ids:
        if chunk_id in still_present:
            pending.append(chunk_id)
        else:
            verified.append(chunk_id)

    logger.info(
        f"[verify-deletion] verified={len(verified)} pending={len(pending)}"
    )
    return {"verified": verified, "pending": pending}
