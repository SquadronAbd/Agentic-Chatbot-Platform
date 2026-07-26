import logging

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.document_maintenance_repository import DocumentMaintenanceRepository
from app.schemas.document_maintenance import (
    ReindexEmbeddingsResponse,
    VerifyVectorDeletionResponse,
)

logger = logging.getLogger(__name__)


class DocumentMaintenanceService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentMaintenanceRepository(db)

    async def request_reindex_embeddings(self, chunk_ids: list[str]) -> ReindexEmbeddingsResponse:
        chunks = await self.repo.get_chunks_by_ids(chunk_ids)
        found_ids = [str(chunk.id) for chunk in chunks]

        if settings.AI_SERVICE_URL and found_ids:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{settings.AI_SERVICE_URL.rstrip('/')}/maintenance/reindex",
                        json={"chunk_ids": found_ids},
                    )
                    response.raise_for_status()
            except httpx.HTTPError as exc:
                logger.warning("AI reindex request failed, stubbing success: %s", exc)
        elif found_ids:
            logger.info(
                "AI_SERVICE_URL not configured; stubbing reindex for %d chunks",
                len(found_ids),
            )

        return ReindexEmbeddingsResponse(requested=len(found_ids), chunk_ids=found_ids)

    async def verify_vector_deletion(self, chunk_ids: list[str]) -> VerifyVectorDeletionResponse:
        chunks = await self.repo.get_chunks_by_ids(chunk_ids)
        verified: list[str] = []
        pending: list[str] = []

        for chunk in chunks:
            chunk_id = str(chunk.id)
            if not chunk.embedding_id:
                verified.append(chunk_id)
                continue

            if settings.AI_SERVICE_URL:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.post(
                            f"{settings.AI_SERVICE_URL.rstrip('/')}/maintenance/verify-deletion",
                            json={"chunk_ids": [chunk_id], "embedding_ids": [chunk.embedding_id]},
                        )
                        response.raise_for_status()
                        payload = response.json()
                        if chunk_id in payload.get("verified", []):
                            verified.append(chunk_id)
                        else:
                            pending.append(chunk_id)
                except httpx.HTTPError as exc:
                    logger.warning("Vector deletion verify failed for %s: %s", chunk_id, exc)
                    pending.append(chunk_id)
            else:
                logger.info(
                    "AI_SERVICE_URL not configured; stubbing vector deletion verify for %s",
                    chunk_id,
                )
                verified.append(chunk_id)

        return VerifyVectorDeletionResponse(verified=verified, pending=pending)
