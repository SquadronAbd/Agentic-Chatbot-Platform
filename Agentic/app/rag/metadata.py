from pathlib import Path
from langchain_core.documents import Document


class MetadataExtractor:
    """
    Adds useful metadata to every document.
    """

    @staticmethod
    def enrich(
        documents: list[Document], file_path: str, *, owner_id: str | None = None,
        document_id: str | None = None, filename: str | None = None,
        content_hash: str | None = None,
    ) -> list[Document]:
        path = Path(file_path).resolve()

        enriched = []

        for doc in documents:

            metadata = {
                **doc.metadata,
                "source": str(path),
                "extension": path.suffix,
                "filename": filename or path.name,
            }
            if owner_id:
                metadata["owner_id"] = str(owner_id)
            if document_id:
                metadata["document_id"] = str(document_id)
            if content_hash:
                metadata["content_hash"] = content_hash

            enriched.append(
                Document(
                    page_content=doc.page_content,
                    metadata=metadata,
                )
            )

        return enriched
