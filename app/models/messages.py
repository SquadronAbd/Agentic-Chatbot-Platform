import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

message_chunks = Table(
    "message_chunks", 
    Base.metadata, 
    Column("message_id", UUID(as_uuid=True), ForeignKey("messages.id"), primary_key=True),
    Column("chunk_id", UUID(as_uuid=True), ForeignKey("document_chunks.id"), primary_key=True)
)

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    tokens = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    retrieved_chunks = relationship("DocumentChunk", secondary=message_chunks)