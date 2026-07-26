from app.router.intent_classifier import IntentClassifier


class RouterAgent:
    """
    Routes the user question
    to the correct agent.
    """

    def __init__(self):

        self.classifier = IntentClassifier()

    def route(
        self,
        question: str,
    ) -> str:

        intent = self.classifier.classify(question)

        return intent.value