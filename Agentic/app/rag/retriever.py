from langchain_core.documents import Document

from app.models.vector_store import vector_store


class DocumentRetriever:
    """
    Retrieves the most relevant document chunks
    from ChromaDB using semantic similarity.
    """

    def __init__(self, k: int = 3):
        self.k = k

    def retrieve(self, query: str) -> list[Document]:
        """
        Perform similarity search.

        Args:
            query: User question

        Returns:
            List of relevant documents
        """

        results = vector_store.similarity_search(
            query=query,
            k=self.k,
        )

        return results


# ---------------------------------------------------
# Singleton Instance
# ---------------------------------------------------

retriever = DocumentRetriever()