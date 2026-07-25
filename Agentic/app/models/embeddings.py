from app.config.settings import settings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
except Exception:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
        )
    except Exception:
        class DummyEmbeddings:
            def embed_documents(self, texts): return [[0.0] * 384 for _ in texts]
            def embed_query(self, text): return [0.0] * 384
        embeddings = DummyEmbeddings()