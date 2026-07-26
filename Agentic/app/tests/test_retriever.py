from app.rag.retriever import DocumentRetriever

retriever = DocumentRetriever(k=3)

docs = retriever.retrieve(
    "What was Microsoft's revenue?"
)

print("=" * 60)
print("Retrieved:", len(docs))
print("=" * 60)

for i, doc in enumerate(docs, 1):
    print(f"\nChunk {i}\n")
    print(doc.page_content[:800])
    print("\nMetadata:")
    print(doc.metadata)