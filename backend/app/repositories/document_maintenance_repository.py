from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunks import DocumentChunk
from app.models.document_health_runs import DocumentHealthRun
from app.models.documents import Document


class DocumentMaintenanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_chunks_needing_reindex(self) -> list[DocumentChunk]:
        result = await self.db.execute(
            select(DocumentChunk).where(
                (DocumentChunk.embedding_id.is_(None)) | (DocumentChunk.needs_reindex.is_(True))
            )
        )
        return list(result.scalars().all())

    async def get_orphaned_chunks(self) -> list[DocumentChunk]:
        result = await self.db.execute(
            text("""
                SELECT dc.id, dc.document_id, dc.content, dc.chunk_index,
                       dc.page_number, dc.embedding_id, dc.needs_reindex
                FROM document_chunks dc
                LEFT JOIN documents d ON d.id = dc.document_id
                WHERE d.id IS NULL
            """)
        )
        rows = result.mappings().all()
        return [
            DocumentChunk(
                id=row["id"],
                document_id=row["document_id"],
                content=row["content"],
                chunk_index=row["chunk_index"],
                page_number=row["page_number"],
                embedding_id=row["embedding_id"],
                needs_reindex=row["needs_reindex"],
            )
            for row in rows
        ]

    async def get_inconsistent_ready_documents(self) -> list[str]:
        result = await self.db.execute(
            text("""
                SELECT d.id
                FROM documents d
                LEFT JOIN document_chunks dc ON dc.document_id = d.id
                WHERE d.status = 'ready'
                GROUP BY d.id
                HAVING COUNT(dc.id) = 0
                    OR BOOL_OR(dc.embedding_id IS NULL)
            """)
        )
        return [str(row[0]) for row in result.all()]

    async def update_document_chunk_counts(self) -> int:
        result = await self.db.execute(
            text("""
                UPDATE documents d
                SET chunk_count = sub.cnt
                FROM (
                    SELECT d2.id, COUNT(dc.id) AS cnt
                    FROM documents d2
                    LEFT JOIN document_chunks dc ON dc.document_id = d2.id
                    GROUP BY d2.id
                ) sub
                WHERE d.id = sub.id
                  AND d.chunk_count IS DISTINCT FROM sub.cnt
            """)
        )
        await self.db.commit()
        return result.rowcount

    async def flag_documents_inconsistent(self, document_ids: list[str]) -> int:
        if not document_ids:
            return 0
        result = await self.db.execute(
            update(Document)
            .where(Document.id.in_(document_ids))
            .values(status="inconsistent")
        )
        await self.db.commit()
        return result.rowcount

    async def delete_chunks_by_ids(self, chunk_ids: list[str]) -> int:
        if not chunk_ids:
            return 0
        result = await self.db.execute(
            delete(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        )
        await self.db.commit()
        return result.rowcount

    async def get_chunks_by_ids(self, chunk_ids: list[str]) -> list[DocumentChunk]:
        if not chunk_ids:
            return []
        result = await self.db.execute(
            select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        )
        return list(result.scalars().all())

    async def record_health_run(
        self,
        *,
        run_date,
        reindex_requested: int,
        orphans_found: int,
        orphans_deleted: int,
        inconsistent_flagged: int,
        metadata_updated: int,
        errors: str | None = None,
    ) -> DocumentHealthRun:
        run = DocumentHealthRun(
            run_date=run_date,
            reindex_requested=reindex_requested,
            orphans_found=orphans_found,
            orphans_deleted=orphans_deleted,
            inconsistent_flagged=inconsistent_flagged,
            metadata_updated=metadata_updated,
            errors=errors,
        )
        self.db.add(run)
        await self.db.commit()
        await self.db.refresh(run)
        return run
