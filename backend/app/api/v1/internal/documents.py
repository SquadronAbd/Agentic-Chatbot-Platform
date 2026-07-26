from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import verify_internal_api_key
from app.schemas.document_maintenance import (
    ChunkIdsRequest,
    ReindexEmbeddingsResponse,
    VerifyVectorDeletionResponse,
)
from app.services.document_maintenance_service import DocumentMaintenanceService

router = APIRouter(
    prefix="/internal/documents",
    tags=["internal-documents"],
    dependencies=[Depends(verify_internal_api_key)],
)


@router.post("/reindex-embeddings", response_model=ReindexEmbeddingsResponse)
async def reindex_embeddings(
    payload: ChunkIdsRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DocumentMaintenanceService(db)
    return await service.request_reindex_embeddings(payload.chunk_ids)


@router.post("/verify-vector-deletion", response_model=VerifyVectorDeletionResponse)
async def verify_vector_deletion(
    payload: ChunkIdsRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DocumentMaintenanceService(db)
    return await service.verify_vector_deletion(payload.chunk_ids)
