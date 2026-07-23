import os
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.core.deps import is_privileged
from app.models.users import User
from app.models.documents import Document

UPLOAD_DIR = "uploads"


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def upload(self, current_user: User, file: UploadFile) -> Document:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        safe_name = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # NOTE: this only stores the raw file and a metadata row.
        # Actual chunking + embedding is owned by the RAG/agent teammate,
        # who should flip `status` from "pending" -> "processing" -> "ready".
        return await self.repo.create(str(current_user.id), file.filename, file_path)

    async def list_for_user(self, current_user: User) -> list[Document]:
        if is_privileged(current_user):
            return await self.repo.list_all()
        return await self.repo.list_by_owner(str(current_user.id))

    async def delete(self, current_user: User, document_id: str) -> None:
        doc = await self.repo.get_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if not is_privileged(current_user) and str(doc.owner_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your document")
        await self.repo.delete(doc)