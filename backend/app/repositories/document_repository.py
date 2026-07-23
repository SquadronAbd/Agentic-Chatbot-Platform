from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documents import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, owner_id: str, filename: str, file_path: str) -> Document:
        doc = Document(owner_id=owner_id, filename=filename, file_path=file_path, status="pending")
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