from __future__ import annotations

import re
import time
from functools import lru_cache

import psycopg
from langchain_core.documents import Document
from loguru import logger

from app.config.settings import settings
from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus
from app.rag.reranker import reranker
from app.rag.query_transformer import transformer
from app.rag.retrieval_logger import log_retrieval


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


def _pg_url() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")


def _expand_by_page(reranked: list[Document]) -> tuple[list[Document], bool]:
    """
    For each reranked chunk that has a page_number, fetch all other chunks
    from the same source file and page from pgvector. This gives the LLM
    full page context instead of isolated fragments.

    Only runs when page_number is present (PDFs). Markdown files return as-is.
    Appends page-expanded chunks after the reranked results, deduplicated.
    Returns (final_docs, expansion_fired).
    """
    seen: set[str] = {doc.page_content for doc in reranked}
    expanded: list[Document] = []

    pages: set[tuple[str, int]] = set()
    for doc in reranked:
        source = doc.metadata.get("source")
        page_number = doc.metadata.get("page_number")
        if source and page_number is not None:
            pages.add((source, int(page_number)))

    if not pages:
        return reranked, False

    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                for source, page_number in pages:
                    cur.execute("""
                        SELECT document, cmetadata
                        FROM langchain_pg_embedding
                        WHERE page_number = %s
                          AND cmetadata->>'source' = %s
                        ORDER BY chunk_index
                    """, (page_number, source))
                    for row in cur.fetchall():
                        text, meta = row[0], row[1]
                        if text not in seen:
                            seen.add(text)
                            expanded.append(Document(page_content=text, metadata=meta or {}))
    except Exception as exc:
        logger.warning(f"Page-based expansion failed, skipping: {exc}")

    return reranked + expanded, True


def _check_hnsw() -> bool:
    """Returns True if an HNSW index exists on langchain_pg_embedding."""
    try:
        with psycopg.connect(_pg_url()) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = 'langchain_pg_embedding'
                      AND indexdef LIKE '%hnsw%'
                """)
                return cur.fetchone() is not None
    except Exception:
        return False


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
      6. Page-based context expansion    — pulls full page chunks for PDF results

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

    def retrieve(
        self,
        query: str,
        source_filter: tuple[str, ...] | None = None,
    ) -> list[Document]:
        return self._retrieve_cached(query, source_filter)

    @lru_cache(maxsize=256)
    def _retrieve_cached(
        self,
        query: str,
        source_filter: tuple[str, ...] | None = None,
    ) -> list[Document]:
        return self._retrieve(query, source_filter)

    def _retrieve(
        self,
        query: str,
        source_filter: tuple[str, ...] | None = None,
    ) -> list[Document]:
        pipeline_warnings: list[str] = []

        semantic_weight, bm25_weight = _get_weights(query)
        query_type = "specific_financial" if _SPECIFIC_FINANCIAL.search(query) else "conceptual"

        # --- step-back query (skipped for specific financial queries) ---
        if _SKIP_STEPBACK.search(query):
            abstract_query = query
            use_abstract = False
        else:
            abstract_query = transformer.transform(query)
            use_abstract = abstract_query.lower().strip() != query.lower().strip()

        # Build pgvector metadata filter when source paths are specified.
        pg_filter: dict | None = None
        if source_filter:
            pg_filter = (
                {"source": source_filter[0]}
                if len(source_filter) == 1
                else {"source": {"$in": list(source_filter)}}
            )
        bm25_src_filter = set(source_filter) if source_filter else None

        # --- semantic search ---
        t0 = time.perf_counter()
        try:
            original_semantic = vector_store.similarity_search(
                query=query, k=self.semantic_k, filter=pg_filter
            )
        except Exception as exc:
            logger.error(f"Semantic search failed: {exc}")
            pipeline_warnings.append(f"Semantic search failed: {exc}")
            original_semantic = []

        abstract_semantic: list[Document] = []
        if use_abstract:
            try:
                abstract_semantic = vector_store.similarity_search(
                    query=abstract_query, k=self.semantic_k // 2, filter=pg_filter
                )
            except Exception as exc:
                logger.warning(f"Abstract semantic search failed: {exc}")
                pipeline_warnings.append(f"Abstract semantic search failed: {exc}")

        semantic_results = _dedup_semantic(original_semantic + abstract_semantic)
        t_semantic = time.perf_counter() - t0

        # --- BM25 search ---
        t0 = time.perf_counter()
        original_bm25 = bm25_corpus.search(query, k=self.bm25_k, source_filter=bm25_src_filter)
        abstract_bm25: list[tuple[Document, float]] = []
        if use_abstract:
            abstract_bm25 = bm25_corpus.search(abstract_query, k=self.bm25_k // 2, source_filter=bm25_src_filter)
        bm25_results = _dedup_bm25(original_bm25 + abstract_bm25)
        t_bm25 = time.perf_counter() - t0

        if not semantic_results and not bm25_results:
            return []

        # --- weighted RRF merge ---
        t0 = time.perf_counter()
        if not bm25_results:
            candidates = semantic_results
        elif not semantic_results:
            candidates = [doc for doc, _ in bm25_results]
        else:
            candidates = _rrf_merge(
                semantic_results, bm25_results, semantic_weight, bm25_weight
            )
        t_rrf = time.perf_counter() - t0

        # --- cross-encoder re-rank ---
        t0 = time.perf_counter()
        reranked = reranker.rerank(query, candidates)
        t_rerank = time.perf_counter() - t0

        # --- page-based context expansion ---
        t0 = time.perf_counter()
        final_docs, page_expansion_fired = _expand_by_page(reranked)
        t_page_expand = time.perf_counter() - t0

        # --- log retrieval ----
        log_retrieval(
            t_semantic=t_semantic,
            t_bm25=t_bm25,
            t_rrf=t_rrf,
            t_rerank=t_rerank,
            t_page_expand=t_page_expand,
            hnsw_used=_check_hnsw(),
            candidate_count=len(candidates),
            top_chunks=[doc.page_content for doc in reranked[:3]],
            page_expansion_fired=page_expansion_fired,
            count_before_expansion=len(reranked),
            count_after_expansion=len(final_docs),
            original_query=query,
            abstract_query=abstract_query,
            use_abstract=use_abstract,
            semantic_weight=semantic_weight,
            bm25_weight=bm25_weight,
            query_type=query_type,
            count_semantic=len(semantic_results),
            count_bm25=len(bm25_results),
            count_rrf=len(candidates),
            count_reranked=len(reranked),
            warnings=pipeline_warnings,
        )

        return final_docs


retriever = HybridRetriever()
