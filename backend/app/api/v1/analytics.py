from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import require_role
from app.core.cache import get_cached, set_cached
from app.core.rate_limiter import rate_limit
from app.models.users import User
from app.models.dag_chat_metrics import DailyChatMetric
import uuid
from datetime import date
from pydantic import BaseModel


class DailyChatMetricOut(BaseModel):
    id: uuid.UUID
    date: date
    user_id: uuid.UUID | None
    message_count: int
    avg_tokens: float
    p95_latency_ms: float
    daily_active_users: int

    class Config:
        from_attributes = True


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily", response_model=list[DailyChatMetricOut])
async def get_daily_metrics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
    _: None = Depends(rate_limit),
):
    cache_key = "analytics:daily_metrics"
    cached = await get_cached(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(DailyChatMetric).order_by(DailyChatMetric.date.desc()).limit(30)
    )
    metrics = list(result.scalars().all())

    # Cache for 5 minutes — analytics don't need real-time freshness
    serializable = [DailyChatMetricOut.model_validate(m).model_dump(mode="json") for m in metrics]
    await set_cached(cache_key, serializable, ttl=300)

    return metrics