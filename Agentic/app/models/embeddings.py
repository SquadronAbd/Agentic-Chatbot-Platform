try:
    from langchain.embeddings.cache import CacheBackedEmbeddings
except ImportError:
    from langchain.embeddings import CacheBackedEmbeddings

try:
    from langchain.storage import LocalFileStore
except ImportError:
    from langchain_community.storage import LocalFileStore

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

# Cache document and query embeddings on disk so identical text is never
# re-encoded. Keyed by content hash; namespace prevents collisions if the
# model is ever swapped.
_store = LocalFileStore("/tmp/embedding_cache")
embeddings = CacheBackedEmbeddings.from_bytes_store(
    _underlying,
    _store,
    namespace=settings.EMBEDDING_MODEL,
    query_embedding_cache=True,
)