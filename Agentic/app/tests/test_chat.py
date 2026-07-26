from app.rag.rag_service import RAGService

service = RAGService()

session_id = "abdullah"

questions = [
    "What company is this report about?",
    "Explain it in simple words.",
    "What is mentioned about covid?",
]

for question in questions:

    result = service.ask(
        session_id=session_id,
        question=question,
    )

    print("=" * 60)
    print("USER")
    print("=" * 60)
    print(question)

    print()

    print("=" * 60)
    print("ASSISTANT")
    print("=" * 60)
    print(result["answer"])

    print()

    print("Messages:", result["messages"])