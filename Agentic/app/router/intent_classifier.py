from enum import Enum
from typing import Any

from app.models.llm import llm


class QueryType(str, Enum):
    MEMORY = "memory"
    DOCUMENT = "document"
    GENERAL = "general"


class IntentClassifier:
    """
    Uses the LLM to classify the user's intent.

    Returns one of:
    - memory
    - document
    - general
    """

    def _extract_text(self, response: Any) -> str:

        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):

            texts = []

            for part in content:

                if isinstance(part, dict):

                    text = part.get("text")

                    if text:
                        texts.append(text)

            return "\n".join(texts).strip()

        return str(content)

    def classify(
        self,
        question: str,
    ) -> QueryType:

        prompt = f"""
You are an intent classifier.

Classify the user's question into EXACTLY ONE category.

Categories:

memory
- Questions about previous conversation
- Chat history
- Previous answers
- Remembering information
- Conversation summary

Examples:
"What did I ask?"
"What did you say?"
"Summarize our conversation."

document
- Questions answered using retrieved documents

Examples:
"What is RAG?"
"Explain LangGraph."
"What technologies does RAG combine?"

general
- Greetings
- Casual conversation
- Creative writing
- Coding help
- Math
- Anything not requiring memory or document retrieval

Examples:
"Hello"
"Write a poem."
"Tell me a joke."

Return ONLY ONE WORD:

memory
document
general

Question:

{question}
"""

        response = llm.invoke(prompt)

        result = self._extract_text(response).lower().strip()

        if "memory" == result:
            return QueryType.MEMORY

        if "document" == result:
            return QueryType.DOCUMENT

        return QueryType.GENERAL