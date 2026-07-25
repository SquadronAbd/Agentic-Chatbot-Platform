from fastapi import Depends, HTTPException, Request, status
from app.core.redis_client import redis_client

RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60


async def rate_limit(request: Request) -> None:
    """
    Per-IP rate limiter — use as a FastAPI dependency directly on route functions.
    Add `_: None = Depends(rate_limit)` to any endpoint you want to throttle.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"

    try:
        current = await redis_client.get(key)
        if current is None:
            await redis_client.set(key, 1, ex=RATE_LIMIT_WINDOW_SECONDS)
        elif int(current) >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: max {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW_SECONDS}s",
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        else:
            await redis_client.incr(key)
    except HTTPException:
        raise
    except Exception:
        # If Redis is down, fail open (don't block legitimate users just because cache is unavailable)
        pass