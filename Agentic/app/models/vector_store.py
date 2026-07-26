from app.config.settings import settings
from app.models.embeddings import embeddings

try:
    from langchain_postgres import PGVector
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=settings.COLLECTION_NAME,
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )
except Exception:
    try:
        from langchain_community.vectorstores import PGVector
        vector_store = PGVector(
            embedding_function=embeddings,
            collection_name=settings.COLLECTION_NAME,
            connection_string=settings.DATABASE_URL,
        )
    except Exception:
        # Fallback dummy vector store for offline/standalone test environments
        class DummyVectorStore:
            def add_documents(self, docs): return len(docs)
            def similarity_search(self, query, k=3): return []
            def as_retriever(self, **kwargs):
                class DummyRetriever:
                    def invoke(self, q): return []
                    def get_relevant_documents(self, q): return []
                return DummyRetriever()
        vector_store = DummyVectorStore()