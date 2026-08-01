from __future__ import annotations
from typing import Optional

import psycopg
from langchain_core.documents import Document
from loguru import logger
from rank_bm25 import BM25Okapi


class BM25Corpus:
    """
    Singleton in-memory BM25 index over all ingested document chunks.

    Lifecycle:
    - Updated immediately when Pipeline.ingest() adds new chunks.
    - Bootstrapped from PGVector's embedding table on startup so the index
      survives service restarts.
    - Falls back to empty (semantic-only search) if bootstrap fails.
    """

    _instance: Optional[BM25Corpus] = None

    def __new__(cls) -> BM25Corpus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._documents: list[Document] = []
            cls._instance._bm25: Optional[BM25Okapi] = None
        return cls._instance

    def add(self, documents: list[Document]) -> None:
        self._documents.extend(documents)
        self._rebuild()

    def search(
        self,
        query: str,
        k: int = 20,
        source_filter: set[str] | None = None,
    ) -> list[tuple[Document, float]]:
        if not self._bm25 or not self._documents:
            return []
        tokenized = query.lower().split()
        scores = self._bm25.get_scores(tokenized)
        # Oversample when filtering so we still get k results after the source check.
        oversample = k * 5 if source_filter else k
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:oversample]
        results = [(self._documents[i], float(scores[i])) for i in top_indices]
        if source_filter:
            results = [
                (doc, score) for doc, score in results
                if doc.metadata.get("source") in source_filter
            ]
        return results[:k]

    @property
    def size(self) -> int:
        return len(self._documents)

    def bootstrap(self, connection_url: str, collection_name: str) -> None:
        """
        Loads existing chunks from PGVector on startup.
        Uses langchain_postgres internal schema (langchain_pg_embedding /
        langchain_pg_collection).  Non-fatal on failure.
        """
        try:
            url = connection_url.replace("postgresql+psycopg://", "postgresql://")
            with psycopg.connect(url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT e.document, e.cmetadata
                        FROM langchain_pg_embedding e
                        JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                        WHERE c.name = %s
                        """,
                        (collection_name,),
                    )
                    rows = cur.fetchall()

            docs = [
                Document(page_content=row[0], metadata=row[1] or {})
                for row in rows
                if row[0]
            ]
            if docs:
                self._documents = docs
                self._rebuild()
                logger.info(f"BM25 corpus bootstrapped with {len(docs)} chunks")
            else:
                logger.info("BM25 corpus: no existing chunks found in PGVector")
        except Exception as exc:
            logger.warning(f"BM25 bootstrap skipped — hybrid search degraded to semantic-only: {exc}")

    def remove_by_source(self, source: str) -> int:
        """Remove all chunks whose metadata['source'] matches source and rebuild index."""
        before = len(self._documents)
        self._documents = [d for d in self._documents if d.metadata.get("source") != source]
        removed = before - len(self._documents)
        if removed:
            self._rebuild()
        return removed

    def _rebuild(self) -> None:
        tokenized = [doc.page_content.lower().split() for doc in self._documents]
        self._bm25 = BM25Okapi(tokenized)


bm25_corpus = BM25Corpus()
