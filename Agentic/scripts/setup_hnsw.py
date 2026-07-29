"""
setup_hnsw.py

Run once after ingestion to:
  1. Create the HNSW index on langchain_pg_embedding (financial_rag DB)
  2. Verify consistency between langchain_pg_embedding and document_chunks (chatbot_db)

Usage:
    python backend/scripts/setup_hnsw.py
"""

import os
import sys
import psycopg

RAG_DB = os.getenv(
    "RAG_DB_URL",
    "postgresql://postgres:password@localhost:5432/financial_rag",
)
CHAT_DB = os.getenv(
    "CHAT_DB_URL",
    "postgresql://postgres:password@localhost:5432/chatbot_db",
)


def ensure_hnsw_index(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM pg_indexes
            WHERE tablename = 'langchain_pg_embedding'
              AND indexdef LIKE '%hnsw%'
        """)
        if cur.fetchone():
            print("[HNSW] Index already exists — skipping creation.")
            return

        print("[HNSW] Creating index (this may take a few minutes)...")
        cur.execute("""
            CREATE INDEX langchain_pg_embedding_hnsw_idx
            ON langchain_pg_embedding
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """)
    conn.commit()
    print("[HNSW] Index created successfully.")


def check_hnsw_index(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename = 'langchain_pg_embedding'
              AND indexdef LIKE '%hnsw%'
        """)
        row = cur.fetchone()
        if row:
            print(f"[HNSW] Confirmed index: {row[0]}")
            print(f"       Definition: {row[1]}")
        else:
            print("[HNSW] WARNING: No HNSW index found.")


def check_vector_db(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding WHERE chunk_index IS NOT NULL")
        with_chunk = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM langchain_pg_embedding WHERE embedding IS NOT NULL")
        with_embedding = cur.fetchone()[0]

    print(f"\n[Vector DB] Total chunks         : {total:,}")
    print(f"[Vector DB] With chunk_index      : {with_chunk:,}")
    print(f"[Vector DB] With embeddings       : {with_embedding:,}")

    if total != with_embedding:
        print(f"[Vector DB] WARNING: {total - with_embedding:,} chunks are missing embeddings!")
    else:
        print("[Vector DB] All chunks have embeddings.")

    return total


def check_consistency(rag_conn, total_rag_chunks):
    try:
        with psycopg.connect(CHAT_DB) as chat_conn:
            with chat_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks")
                total_chat = cur.fetchone()[0]

        print(f"\n[Consistency] langchain_pg_embedding : {total_rag_chunks:,}")
        print(f"[Consistency] document_chunks        : {total_chat:,}")

        if total_rag_chunks == total_chat:
            print("[Consistency] Counts match.")
        else:
            diff = abs(total_rag_chunks - total_chat)
            print(f"[Consistency] WARNING: Counts differ by {diff:,}.")
            print("              This is expected if document_chunks tracks metadata separately.")
    except Exception as e:
        print(f"[Consistency] Could not connect to chatbot_db: {e}")
        print("              Skipping cross-database consistency check.")


def main():
    print("=" * 55)
    print("  HNSW Index Setup & Consistency Check")
    print("=" * 55)

    try:
        with psycopg.connect(RAG_DB) as conn:
            ensure_hnsw_index(conn)
            check_hnsw_index(conn)
            total = check_vector_db(conn)

        check_consistency(None, total)

    except psycopg.OperationalError as e:
        print(f"\nERROR: Could not connect to financial_rag DB.\n{e}")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
