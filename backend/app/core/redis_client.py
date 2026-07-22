import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def blocklist_token(jti: str, ttl_seconds: int) -> None:
    """Store a token's unique ID (jti) in Redis until it would have expired anyway."""
    if ttl_seconds > 0:
        await redis_client.set(f"blocklist:{jti}", "1", ex=ttl_seconds)


async def is_token_blocklisted(jti: str) -> bool:
    return await redis_client.exists(f"blocklist:{jti}") == 1