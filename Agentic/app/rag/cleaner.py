import re
from langchain_core.documents import Document


class DocumentCleaner:
    """
    Cleans raw document text before chunking.
    """

    @staticmethod
    def clean(documents: list[Document]) -> list[Document]:
        cleaned_docs = []

        for doc in documents:
            text = doc.page_content

            # Remove extra spaces
            text = re.sub(r"\s+", " ", text)

            # Remove leading/trailing spaces
            text = text.strip()

            cleaned_docs.append(
                Document(
                    page_content=text,
                    metadata=doc.metadata
                )
            )

        return cleaned_docs