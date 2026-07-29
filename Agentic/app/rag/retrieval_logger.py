"""
retrieval_logger.py

Standalone logging module for the hybrid retrieval pipeline.
Writes structured logs to logs/retrieval_YYYY-MM-DD.log with daily rotation
and 7-day retention. Does not touch any retrieval logic.
"""

from pathlib import Path
from loguru import logger as _base_logger

# ── File sink setup ──────────────────────────────────────────────────────────

_LOG_DIR = Path(__file__).resolve().parents[3] / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

retrieval_logger = _base_logger.bind(module="retrieval")

retrieval_logger.add(
    sink=str(_LOG_DIR / "retrieval_{time:YYYY-MM-DD}.log"),
    rotation="00:00",       # new file every day at midnight
    retention="7 days",     # delete logs older than 7 days
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}",
    enqueue=True,
)


# ── Public function ──────────────────────────────────────────────────────────

def log_retrieval(
    *,
    # Stage timings (seconds)
    t_semantic: float,
    t_bm25: float,
    t_rrf: float,
    t_rerank: float,
    t_page_expand: float,
    # HNSW
    hnsw_used: bool,
    # Candidate count entering reranker
    candidate_count: int,
    # Top chunk previews after reranking (list of str)
    top_chunks: list,
    # Page expansion
    page_expansion_fired: bool,
    count_before_expansion: int,
    count_after_expansion: int,
    # Query details
    original_query: str,
    abstract_query: str,
    use_abstract: bool,
    # Weights
    semantic_weight: float,
    bm25_weight: float,
    query_type: str,          # "specific_financial" or "conceptual"
    # Stage counts
    count_semantic: int,
    count_bm25: int,
    count_rrf: int,
    count_reranked: int,
    # Warnings/errors collected during the run
    warnings: list[str] | None = None,
) -> None:

    log = retrieval_logger
    sep = "-" * 60

    log.debug(sep)

    # ── 1. Stage timings ────────────────────────────────────────────────────
    log.debug("STAGE TIMINGS")
    log.debug(f"  Semantic search : {t_semantic:.4f}s")
    log.debug(f"  BM25 search     : {t_bm25:.4f}s")
    log.debug(f"  RRF merge       : {t_rrf:.4f}s")
    log.debug(f"  Reranking       : {t_rerank:.4f}s")
    log.debug(f"  Page expansion  : {t_page_expand:.4f}s")
    log.debug(f"  Total           : {t_semantic + t_bm25 + t_rrf + t_rerank + t_page_expand:.4f}s")

    # ── 2. HNSW index ───────────────────────────────────────────────────────
    if hnsw_used:
        log.info("HNSW index      : YES (index scan confirmed)")
    else:
        log.warning("HNSW index      : NO — sequential scan detected; index may be missing")

    # ── 3. Candidate count ──────────────────────────────────────────────────
    log.info(f"Candidates into reranker: {candidate_count}")
    if candidate_count > 30:
        log.warning(f"Candidate count is high ({candidate_count}); reranker latency may be affected")

    # ── 4. Top chunk previews ───────────────────────────────────────────────
    log.debug("TOP CHUNKS AFTER RERANKING")
    for i, chunk in enumerate(top_chunks[:3], start=1):
        preview = str(chunk)[:150].replace("\n", " ")
        log.debug(f"  Top chunk {i}: {preview}")

    # ── 5. Page expansion ───────────────────────────────────────────────────
    if page_expansion_fired:
        log.info(
            f"Page expansion  : FIRED | "
            f"before={count_before_expansion} after={count_after_expansion} "
            f"(+{count_after_expansion - count_before_expansion} chunks)"
        )
    else:
        log.warning("Page expansion  : SKIPPED — no page_number in chunk metadata (markdown files)")

    # ── 6. Query details ────────────────────────────────────────────────────
    log.info(f"Original query  : {original_query}")
    log.info(f"Abstract query  : {abstract_query}")
    log.info(f"Step-back used  : {use_abstract}")
    if not use_abstract:
        log.warning("Step-back query did not diverge — step-back is providing no benefit")

    # ── Supporting info ─────────────────────────────────────────────────────
    log.info(
        f"Query type      : {query_type} | "
        f"semantic_weight={semantic_weight} bm25_weight={bm25_weight}"
    )
    log.info(
        f"Stage counts    : "
        f"semantic={count_semantic} → bm25={count_bm25} → rrf={count_rrf} → "
        f"reranked={count_reranked} → final={count_after_expansion}"
    )

    if warnings:
        for w in warnings:
            log.warning(f"Pipeline warning: {w}")

    log.debug(sep)
