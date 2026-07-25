from app.rag.retriever import DocumentRetriever


class RetrieverTool:
    """
    Tool for semantic document retrieval.
    """

    def __init__(self, k: int = 3):
        self.retriever = DocumentRetriever(k=k)

    def search(self, query: str):

        documents = self.retriever.retrieve(query)

        return {
            "success": True,
            "count": len(documents),
            "documents": documents,
        }