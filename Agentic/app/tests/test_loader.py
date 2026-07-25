from app.rag.loader import DocumentLoader

docs = DocumentLoader.load("documents/sample.txt")

print(f"Loaded {len(docs)} document(s)\n")

for doc in docs:
    print(doc.page_content)
    print("-" * 60)