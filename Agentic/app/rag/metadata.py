from pathlib import Path
from langchain_core.documents import Document


class MetadataExtractor:
    """
    Adds useful metadata to every document.
    """

    @staticmethod
    def enrich(documents: list[Document], file_path: str):
        path = Path(file_path)

        enriched = []

        for doc in documents:

            metadata = {
                **doc.metadata,
                "source": path.name,
                "extension": path.suffix,
            }

            enriched.append(
                Document(
                    page_content=doc.page_content,
                    metadata=metadata,
                )
            )

        return enriched