from app.router.intent_classifier import IntentClassifier

classifier = IntentClassifier()

questions = [

    "What is Retrieval-Augmented Generation?",

    "Explain LangGraph.",

    "Who are we talking about?",

    "What did I ask previously?",

    "Summarize our conversation.",

    "Hello",

    "Tell me a joke.",

    "Write Python code.",

]

for question in questions:

    print("=" * 60)
    print(question)

    result = classifier.classify(question)

    print(result.value)