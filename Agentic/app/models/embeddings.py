from app.config.settings import settings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

_underlying = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 128},
    # Asymmetric embedding: BGE models expect a retrieval prefix on the query side
    # but no prefix for document passages — this improves recall at query time.
    query_instruction="Represent this sentence for searching relevant passages: ",
)

# Wrap with disk-backed cache so identical text is never re-encoded.
# Tries multiple import paths to handle LangChain version differences.
# Falls back to the underlying embedder if caching cannot be set up.
try:
    try:
        from langchain.embeddings.cache import CacheBackedEmbeddings
    except ImportError:
        from langchain.embeddings import CacheBackedEmbeddings

    try:
        from langchain.storage import LocalFileStore
    except ImportError:
        from langchain_community.storage import LocalFileStore

    _store = LocalFileStore("/tmp/embedding_cache")
    embeddings = CacheBackedEmbeddings.from_bytes_store(
        _underlying,
        _store,
        namespace=settings.EMBEDDING_MODEL,
        query_embedding_cache=True,
    )
except Exception:
    embeddings = _underlying
