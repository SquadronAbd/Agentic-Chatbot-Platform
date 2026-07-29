from __future__ import annotations

import re
from functools import lru_cache

from langchain_core.documents import Document
from loguru import logger

from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus
from app.rag.reranker import reranker
from app.rag.query_transformer import transformer


_RRF_K = 60

# Matches financial queries that contain specific values — these benefit
# from higher BM25 weight since exact keyword matching finds precise figures.
_SPECIFIC_FINANCIAL = re.compile(
    r"\$[\d,.]+|"           # dollar amounts:  $1.2B, $450,000
    r"\d+\.?\d*\s*%|"      # percentages:     12.5%, 3%
    r"\bQ[1-4]\b|"         # quarters:        Q1, Q3
    r"\bFY\s*\d{2,4}\b|"   # fiscal years:    FY2024, FY23
    r"\b[A-Z]{2,5}\b"      # tickers/acronyms: AAPL, EBITDA, EPS, GAAP
)

# Queries matching this pattern are specific enough that step-back abstraction
# won't improve recall — skip the transformer LLM call for these.
_SKIP_STEPBACK = re.compile(
    r"\$[\d,.]+|"           # dollar amounts
    r"\d+\.?\d*\s*%|"      # percentages
    r"\bQ[1-4]\s*\d{4}\b|" # Q3 2024 style
    r"\bFY\s*\d{2,4}\b|"   # FY2024
    r"\b(20\d{2}|19\d{2})\b.*\b(revenue|profit|loss|income|ebitda|eps)\b|"
    r"\b(revenue|profit|loss|income|ebitda|eps)\b.*\b(20\d{2}|19\d{2})\b",
    re.I,
)


def _get_weights(query: str) -> tuple[float, float]:
    """
    Returns (semantic_weight, bm25_weight).

    Default α=0.7, β=0.3 follows the well-validated production formula for
    financial corpora where most questions are conceptual.  Queries containing
    specific financial values (dollar amounts, percentages, quarters, tickers,
    financial acronyms) flip the weights to favour BM25 since exact keyword
    matching finds precise figures more reliably than dense similarity.
    """
    if _SPECIFIC_FINANCIAL.search(query):
        return 0.3, 0.7
    return 0.7, 0.3


def _rrf_merge(
    semantic: list[Document],
    bm25: list[tuple[Document, float]],
    semantic_weight: float,
    bm25_weight: float,
) -> list[Document]:
    """
    Weighted Reciprocal Rank Fusion over semantic and BM25 result lists.
    Deduplicates by page_content.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, doc in enumerate(semantic):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + semantic_weight / (_RRF_K + rank + 1)
        doc_map[key] = doc

    for rank, (doc, _) in enumerate(bm25):
        key = doc.page_content
        scores[key] = scores.get(key, 0.0) + bm25_weight / (_RRF_K + rank + 1)
        doc_map[key] = doc

    return [doc_map[k] for k in sorted(scores, key=lambda k: scores[k], reverse=True)]


def _dedup_semantic(docs: list[Document]) -> list[Document]:
    seen: set[str] = set()
    out: list[Document] = []
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            out.append(doc)
    return out


def _dedup_bm25(results: list[tuple[Document, float]]) -> list[tuple[Document, float]]:
    seen: set[str] = set()
    out: list[tuple[Document, float]] = []
    for doc, score in results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            out.append((doc, score))
    return out


class HybridRetriever:
    """
    Full retrieval pipeline:

      1. Step-back query transformation  — generates a broader abstract query
                                           alongside the original
      2. PGVector semantic search        — on both original + abstract queries
      3. BM25 keyword search             — on both original + abstract queries
      4. Weighted RRF merge              — weights dynamically set based on
                                           whether the query contains specific
                                           financial figures or is conceptual
      5. Cross-encoder re-ranking        — final precision pass

    Degrades gracefully at every step: failed step-back → original query only;
    empty BM25 corpus → semantic only; unavailable re-ranker → RRF order kept.
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
        return self._retrieve_cached(query)

    @lru_cache(maxsize=256)
    def _retrieve_cached(self, query: str) -> list[Document]:
        return self._retrieve(query)

    def _retrieve(self, query: str) -> list[Document]:
        semantic_weight, bm25_weight = _get_weights(query)

        # --- step-back query (skipped for specific financial queries) ---
        if _SKIP_STEPBACK.search(query):
            abstract_query = query
            use_abstract = False
        else:
            abstract_query = transformer.transform(query)
            use_abstract = abstract_query.lower().strip() != query.lower().strip()

        # --- semantic search ---
        try:
            original_semantic = vector_store.similarity_search(
                query=query, k=self.semantic_k
            )
        except Exception as exc:
            logger.error(f"Semantic search failed: {exc}")
            original_semantic = []

        abstract_semantic: list[Document] = []
        if use_abstract:
            try:
                abstract_semantic = vector_store.similarity_search(
                    query=abstract_query, k=self.semantic_k // 2
                )
            except Exception as exc:
                logger.warning(f"Abstract semantic search failed: {exc}")

        semantic_results = _dedup_semantic(original_semantic + abstract_semantic)

        # --- BM25 search ---
        original_bm25 = bm25_corpus.search(query, k=self.bm25_k)
        abstract_bm25: list[tuple[Document, float]] = []
        if use_abstract:
            abstract_bm25 = bm25_corpus.search(abstract_query, k=self.bm25_k // 2)

        bm25_results = _dedup_bm25(original_bm25 + abstract_bm25)

        if not semantic_results and not bm25_results:
            return []

        # --- weighted RRF merge ---
        if not bm25_results:
            candidates = semantic_results
        elif not semantic_results:
            candidates = [doc for doc, _ in bm25_results]
        else:
            candidates = _rrf_merge(
                semantic_results, bm25_results, semantic_weight, bm25_weight
            )

        # --- cross-encoder re-rank ---
        return reranker.rerank(query, candidates)


retriever = HybridRetriever()
