from app.rag.loader import DocumentLoader

loader = DocumentLoader()

docs = loader.load(
    "documents/financial_reports/report1.md"
)

print("=" * 60)
print("DOCUMENTS")
print("=" * 60)

print(len(docs))

print()

print(docs[0].page_content[:1000])