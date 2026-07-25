from app.rag.rag_service import RAGService

service = RAGService()

session = "abdullah"

questions = [

    "What is Retrieval-Augmented Generation?",

    "Explain it in simple words.",

    "Which technologies does it combine?",

    "What is LangGraph?",

    "Explain it simply.",

    "Who is this conversation about?",

]

for question in questions:

    print("=" * 60)
    print("USER")
    print("=" * 60)
    print(question)

    response = service.ask(
        session_id=session,
        question=question,
    )

    print()
    print("=" * 60)
    print("ASSISTANT")
    print("=" * 60)
    print(response["answer"])

    print()
    print("Messages:", response["messages"])