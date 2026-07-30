import os
import uuid
import httpx

from fastapi import HTTPException, UploadFile, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.document_repository import DocumentRepository
from app.core.deps import is_privileged
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.users import User
from app.models.documents import Document

UPLOAD_DIR = "uploads"


async def _run_ingestion(document_id: str, file_path: str, filename: str) -> None:
    """Background task: call agentic /ingest and update document status."""
    async with AsyncSessionLocal() as db:
        repo = DocumentRepository(db)
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                with open(file_path, "rb") as f:
                    response = await client.post(
                        f"{settings.AI_SERVICE_URL}/ingest",
                        files={"file": (filename, f, "application/octet-stream")},
                    )

            if response.status_code != 200:
                await repo.update_status(document_id, "error")
                return

            chunk_count = response.json().get("chunks", 0)
            await repo.update_status(document_id, "ready", chunk_count=chunk_count)

        except Exception:
            await repo.update_status(document_id, "error")


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def upload(
        self, current_user: User, file: UploadFile, background_tasks: BackgroundTasks
    ) -> Document:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = file.filename or "untitled"
        safe_name = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Save record immediately with status "processing" so the UI can show progress.
        doc = await self.repo.create(
            str(current_user.id),
            filename,
            file_path,
            chunk_count=0,
            status="processing",
        )

        # Run the heavy agentic ingestion in the background.
        background_tasks.add_task(
            _run_ingestion, str(doc.id), file_path, filename
        )

        return doc

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

        path = getattr(doc, "file_path", None)
        if path and isinstance(path, (str, bytes)) and os.path.exists(path):
            os.remove(path)

        await self.repo.delete(doc)
