import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Column, Date, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class DocumentHealthRun(Base):
    __tablename__ = "document_health_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_date = Column(Date, nullable=False)
    reindex_requested = Column(Integer, default=0, nullable=False)
    orphans_found = Column(Integer, default=0, nullable=False)
    orphans_deleted = Column(Integer, default=0, nullable=False)
    inconsistent_flagged = Column(Integer, default=0, nullable=False)
    metadata_updated = Column(Integer, default=0, nullable=False)
    errors = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
