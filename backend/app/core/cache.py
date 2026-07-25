import json
from typing import Any
from app.core.redis_client import redis_client

DEFAULT_TTL = 300  # 5 minutes


async def get_cached(key: str) -> Any | None:
    """Retrieve a cached value from Redis. Returns None if not found."""
    value = await redis_client.get(f"cache:{key}")
    if value:
        return json.loads(value)
    return None


async def set_cached(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a value in Redis cache with a TTL."""
    await redis_client.set(f"cache:{key}", json.dumps(value, default=str), ex=ttl)


async def invalidate_cache(key: str) -> None:
    """Remove a cached value — call this whenever underlying data changes."""
    await redis_client.delete(f"cache:{key}")