import uuid

from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class AgentTool(Base):
    __tablename__ = "agent_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, nullable=True) 