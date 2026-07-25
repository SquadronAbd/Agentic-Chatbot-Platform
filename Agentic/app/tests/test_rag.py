from app.rag.rag_service import RAGService

service = RAGService()

question = "What is Retrieval-Augmented Generation?"

result = service.ask(question)

print("=" * 60)
print("QUESTION")
print("=" * 60)
print(result["question"])

print()

print("=" * 60)
print("ANSWER")
print("=" * 60)
print(result["answer"])

print()

print("=" * 60)
print("SOURCES")
print("=" * 60)

for source in result["sources"]:
    print(source["source"])