from app.rag.retriever import retriever


class RetrieverTool:
    """
    Tool for hybrid document retrieval (dense + BM25 + re-ranking).
    """

    def search(
        self,
        query: str,
        source_filter: tuple[str, ...] | None = None,
    ) -> dict:
        documents = retriever.retrieve(query, source_filter=source_filter)
        return {
            "success": True,
            "count": len(documents),
            "documents": documents,
        }
