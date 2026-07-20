import uuid
from datetime import date as date_type

from sqlalchemy import Column, Date, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class DailyChatMetric(Base):
    __tablename__ = "daily_chat_metrics"
    __table_args__ = (UniqueConstraint("date", "user_id", name="uq_date_user"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message_count = Column(Integer, default=0)
    avg_tokens = Column(Float, default=0)
    p95_latency_ms = Column(Float, default=0)
    daily_active_users = Column(Integer, default=0)