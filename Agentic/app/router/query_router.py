from enum import Enum


class QueryType(str, Enum):
    MEMORY = "memory"
    DOCUMENT = "document"
    GENERAL = "general"


class QueryRouter:

    MEMORY_PHRASES = [

        "what did i ask",

        "what did i say",

        "who are we talking about",

        "our conversation",

        "this conversation",

        "previous answer",

        "last answer",

        "remember",

        "conversation summary",

        "summarize our conversation",

        "what were we discussing",

    ]

    DOCUMENT_KEYWORDS = [

        "what",

        "who",

        "when",

        "where",

        "why",

        "how",

        "define",

        "describe",

        "explain",

    ]

    def classify(self, question: str) -> QueryType:

        text = question.lower().strip()

        # -------------------------------------
        # Conversation Intent
        # -------------------------------------

        for phrase in self.MEMORY_PHRASES:

            if phrase in text:
                return QueryType.MEMORY

        # -------------------------------------
        # Document Intent
        # -------------------------------------

        for keyword in self.DOCUMENT_KEYWORDS:

            if text.startswith(keyword):
                return QueryType.DOCUMENT

        # -------------------------------------
        # General
        # -------------------------------------

        return QueryType.GENERAL