from app.router.query_router import QueryRouter

router = QueryRouter()

questions = [

    "What is RAG?",

    "Explain LangGraph.",

    "Who are we talking about?",

    "Summarize our conversation.",

    "What did I ask before?",

    "Tell me a joke.",

    "Hello",

    "Good morning",

]

for question in questions:

    print("=" * 60)
    print(question)
    print(router.classify(question).value)