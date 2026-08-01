from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Header, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import require_role
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.models.users import User
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    return await service.upload(current_user, file, background_tasks)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    return await service.list_for_user(current_user)


@router.patch("/internal/{document_id}/status", include_in_schema=False)
async def internal_update_status(
    document_id: str,
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
    body: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    repo = DocumentRepository(db)
    await repo.update_status(document_id, body["status"], chunk_count=body.get("chunk_count"))
    return {"ok": True}


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    await service.delete(current_user, document_id)
    return None