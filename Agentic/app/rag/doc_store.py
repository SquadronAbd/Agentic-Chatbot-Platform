"""
doc_store.py — tracks which document source paths belong to each user.

Stored in Redis as a SET under `user:{owner_id}:doc_sources` with a 24-hour TTL.
Falls back gracefully if Redis is unavailable (returns empty list).
"""
from __future__ import annotations

from loguru import logger

from app.config.settings import settings

_redis = None
_USER_DOCS_TTL = 86_400  # 24 hours


def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis as _redis_lib
            client = _redis_lib.Redis.from_url(settings.REDIS_URL, decode_responses=True)
            client.ping()
            _redis = client
        except Exception as exc:
            logger.warning("doc_store: Redis unavailable ({}), source filtering disabled", exc)
    return _redis


def add_source(owner_id: str, source_path: str) -> None:
    """Record that owner_id has ingested a document at source_path."""
    if not owner_id or not source_path:
        return
    r = _get_redis()
    if not r:
        return
    key = f"user:{owner_id}:doc_sources"
    try:
        r.sadd(key, source_path)
        r.expire(key, _USER_DOCS_TTL)
        logger.debug("doc_store: added source for user {}: {}", owner_id, source_path)
    except Exception as exc:
        logger.warning("doc_store.add_source failed: {}", exc)


def get_sources(owner_id: str) -> list[str]:
    """Return all source paths ingested by this user (empty list if none or Redis down)."""
    if not owner_id:
        return []
    r = _get_redis()
    if not r:
        return []
    try:
        return list(r.smembers(f"user:{owner_id}:doc_sources"))
    except Exception:
        return []
