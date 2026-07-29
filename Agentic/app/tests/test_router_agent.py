from app.router.intent_classifier import IntentClassifier

classifier = IntentClassifier()

questions = [
    "What company is this report about?",
    "What did I ask previously?",
    "What is AI?",
]

for question in questions:
    print("=" * 60)
    print(question)
    print(classifier.classify(question).value)
