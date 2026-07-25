from __future__ import annotations

from langchain_core.documents import Document
from loguru import logger

from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus
from app.rag.reranker import reranker


_RRF_K = 60  # standard constant for Reciprocal Rank Fusion


def _rrf_merge(
    semantic: list[Document],
    bm25: list[tuple[Document, float]],
) -> list[Document]:
    """
    Merges semantic and BM25 result lists using Reciprocal Rank Fusion.
    Deduplicates by page_content.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, doc in enumerate(semantic):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + 1.0 / (_RRF_K + rank + 1)
        doc_map[key] = doc

    for rank, (doc, _) in enumerate(bm25):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + 1.0 / (_RRF_K + rank + 1)
        doc_map[key] = doc

    return [doc_map[k] for k in sorted(scores, key=lambda k: scores[k], reverse=True)]


class HybridRetriever:
    """
    Retrieval pipeline:
      1. PGVector semantic search        (dense)
      2. BM25 keyword search             (sparse)
      3. Reciprocal Rank Fusion merge
      4. Cross-encoder re-ranking

    Degrades gracefully: if BM25 corpus is empty (e.g. first startup before
    bootstrap completes), falls back to semantic-only.  If re-ranker is
    unavailable, returns RRF-merged candidates truncated to final_k.
    """

    def __init__(
        self,
        semantic_k: int = 20,
        bm25_k: int = 20,
        final_k: int = 6,
    ) -> None:
        self.semantic_k = semantic_k
        self.bm25_k = bm25_k
        self.final_k = final_k

    def retrieve(self, query: str) -> list[Document]:
        # --- dense retrieval ---
        try:
            semantic_results = vector_store.similarity_search(query=query, k=self.semantic_k)
        except Exception as exc:
            logger.error(f"Semantic search failed: {exc}")
            semantic_results = []

        # --- sparse retrieval ---
        bm25_results = bm25_corpus.search(query, k=self.bm25_k)

        if not semantic_results and not bm25_results:
            return []

        # --- merge ---
        if not bm25_results:
            candidates = semantic_results
        elif not semantic_results:
            candidates = [doc for doc, _ in bm25_results]
        else:
            candidates = _rrf_merge(semantic_results, bm25_results)

        # --- re-rank ---
        return reranker.rerank(query, candidates)


retriever = HybridRetriever()
