import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__=  "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False, default="agent") # admin, manager, agent, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversations = relationship("Conversation", back_populates="user")  # One to Many relation
    documents = relationship("Document", back_populates="owner")
    api_keys = relationship("ApiKey", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")