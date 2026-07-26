from app.rag.loader import DocumentLoader
from app.rag.cleaner import DocumentCleaner
from app.rag.metadata import MetadataExtractor

docs = DocumentLoader.load("documents/sample.txt")

docs = DocumentCleaner.clean(docs)

docs = MetadataExtractor.enrich(
    docs,
    "documents/sample.txt"
)

print()

for doc in docs:

    print(doc.page_content)

    print()

    print(doc.metadata)