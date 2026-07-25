from app.rag.retriever import retriever


class RetrieverTool:
    """
    Tool for hybrid document retrieval (dense + BM25 + re-ranking).
    """

    def search(self, query: str) -> dict:
        documents = retriever.retrieve(query)
        return {
            "success": True,
            "count": len(documents),
            "documents": documents,
        }
