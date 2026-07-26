from app.rag.loader import DocumentLoader
from app.rag.cleaner import DocumentCleaner
from app.rag.metadata import MetadataExtractor
from app.rag.chunker import DocumentChunker

docs = DocumentLoader.load("documents/sample.txt")
docs = DocumentCleaner.clean(docs)
docs = MetadataExtractor.enrich(docs, "documents/sample.txt")

chunker = DocumentChunker(
    chunk_size=100,
    chunk_overlap=20,
)

chunks = chunker.split(docs)

print(f"\nTotal Chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks, start=1):
    print("=" * 60)
    print(f"Chunk {i}")
    print("=" * 60)
    print(chunk.page_content)
    print("\nMetadata:")
    print(chunk.metadata)
    print()