from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_status(
        self, document_id: str, status: str, chunk_count: int | None = None
    ) -> None:
        values: dict = {"status": status}
        if chunk_count is not None:
            values["chunk_count"] = chunk_count
        await self.db.execute(
            update(Document).where(Document.id == document_id).values(**values)
        )
        await self.db.commit()

    async def create(
        self, owner_id: str, filename: str, file_path: str, chunk_count: int = 0, status: str = "processing"
    ) -> Document:
        doc = Document(
            owner_id=owner_id,
            filename=filename,
            file_path=file_path,
            status=status,
            chunk_count=chunk_count,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, document_id: str) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Document]:
        result = await self.db.execute(select(Document))
        return list(result.scalars().all())

    async def list_by_owner(self, owner_id: str) -> list[Document]:
        result = await self.db.execute(select(Document).where(Document.owner_id == owner_id))
        return list(result.scalars().all())

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()