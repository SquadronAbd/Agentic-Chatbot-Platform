"""
One-time ingestion script.

Run this once (or whenever you add new documents) to embed and store
all markdown files from backend/data/markdowns into PGVector.

Usage:
    cd Agentic
    python ingest.py
    python ingest.py --dir ../backend/data/markdowns
    python ingest.py --dir documents/financial_reports --clear
"""

import argparse
import os
import sys
import time

# Ensure the Agentic package is importable when run from the Agentic/ directory
sys.path.insert(0, os.path.dirname(__file__))

from app.rag.pipeline import pipeline
from app.rag.bm25_corpus import bm25_corpus
from app.config.settings import settings
from app.utils.logger import logger


DEFAULT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "backend", "data", "markdowns"
)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into PGVector.")
    parser.add_argument(
        "--dir",
        default=DEFAULT_DIR,
        help="Directory of markdown/PDF files to ingest (default: backend/data/markdowns)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the existing collection before ingesting",
    )
    args = parser.parse_args()

    target = os.path.abspath(args.dir)
    if not os.path.isdir(target):
        logger.error(f"Directory not found: {target}")
        sys.exit(1)

    if args.clear:
        logger.warning(f"Clearing collection '{settings.COLLECTION_NAME}' before ingest...")
        try:
            import psycopg
            url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
            with psycopg.connect(url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM langchain_pg_embedding WHERE collection_id = "
                        "(SELECT uuid FROM langchain_pg_collection WHERE name = %s)",
                        (settings.COLLECTION_NAME,),
                    )
                conn.commit()
            logger.success("Collection cleared.")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            sys.exit(1)

    files = [f for f in os.listdir(target) if f.endswith((".md", ".pdf", ".txt"))]
    logger.info(f"Starting ingestion of {len(files)} files from: {target}")

    start = time.time()
    total_files, total_chunks = pipeline.ingest_directory(target)
    elapsed = time.time() - start

    logger.success(
        f"Done — {total_files} files, {total_chunks} chunks "
        f"in {elapsed/60:.1f} min"
    )

    # Refresh BM25 after ingestion
    bm25_corpus.bootstrap(settings.DATABASE_URL, settings.COLLECTION_NAME)
    logger.info(f"BM25 index refreshed with {bm25_corpus.size} chunks.")


if __name__ == "__main__":
    main()
