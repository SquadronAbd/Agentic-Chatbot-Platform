from app.graph.workflow import graph


questions = [

    "What is Retrieval-Augmented Generation?",

    "Summarize our conversation.",

    "Tell me a joke.",

]


for question in questions:

    print("=" * 60)
    print("QUESTION")
    print("=" * 60)

    print(question)

    state = {

        "session_id": "abdullah",

        "question": question,

        "intent": "",

        "documents": [],

        "answer": "",

        "summary": "",

        "sources": [],

        "memory": None,
    }

    result = graph.invoke(state)

    print()

    print("Intent :", result["intent"])

    print()

    print("Answer :")

    print(result["answer"])

    print()

    print("Retrieved Documents :", len(result["documents"]))

    print("\n")