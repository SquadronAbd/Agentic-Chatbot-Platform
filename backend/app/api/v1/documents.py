from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.services.document_service import DocumentService
from app.models.users import User
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    return await service.upload(current_user, file)


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    return await service.list_for_user(current_user)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = DocumentService(db)
    await service.delete(current_user, document_id)
    return None