import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    filename: str
    status: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True