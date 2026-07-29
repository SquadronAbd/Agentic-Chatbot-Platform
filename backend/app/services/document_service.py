import os
import uuid
import httpx

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.core.deps import is_privileged
from app.core.config import settings
from app.models.users import User
from app.models.documents import Document

UPLOAD_DIR = "uploads"

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def upload(self, current_user: User, file: UploadFile) -> Document:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = file.filename or "untitled"
        safe_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                with open(file_path, "rb") as uploaded_file:
                    response = await client.post(
                        f"{settings.AI_SERVICE_URL}/ingest",
                        files={
                            "file": (
                                filename,
                                uploaded_file,
                                file.content_type,
                            )
                        },
                    )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"AI ingestion failed: {response.text}",
                )

            print(f"\n===== AI INGESTION =====\n{response.json()}\n========================\n")

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to connect to AI Module: {str(e)}",
            )

        return await self.repo.create(
            str(current_user.id),
            filename,
            file_path,
        )

    async def list_for_user(self, current_user: User) -> list[Document]:
        if is_privileged(current_user):
            return await self.repo.list_all()
        return await self.repo.list_by_owner(str(current_user.id))

    async def delete(self, current_user: User, document_id: str) -> None:
        doc = await self.repo.get_by_id(document_id)

        if doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if not is_privileged(current_user) and str(doc.owner_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your document",
            )

        # doc.file_path may be a SQLAlchemy Column type in some typing contexts;
        # use getattr to safely retrieve the runtime value and guard its type.
        path = getattr(doc, "file_path", None)
        if path and isinstance(path, (str, bytes)) and os.path.exists(path):
            os.remove(path)

        await self.repo.delete(doc)