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
except ImportError:
    from langchain_community.vectorstores import PGVector
    vector_store = PGVector(
        embedding_function=embeddings,
        collection_name=settings.COLLECTION_NAME,
        connection_string=settings.DATABASE_URL,
    )