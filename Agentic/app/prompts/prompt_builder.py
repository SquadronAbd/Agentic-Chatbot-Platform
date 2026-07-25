from langchain_core.documents import Document
from app.memory.conversation import Message


class PromptBuilder:
    """
    Builds prompts for the RAG system.

    The prompt contains:
    1. Conversation summary
    2. Recent conversation
    3. Retrieved document context
    4. Current user question
    """

    @staticmethod
    def _build_context(
        documents: list[Document],
    ) -> str:
        """
        Convert retrieved documents into context.
        """

        if not documents:
            return "No relevant documents were retrieved."

        sections = []

        for index, document in enumerate(documents, start=1):

            source = document.metadata.get("source", "Unknown")

            sections.append(
                f"""Document {index}
Source: {source}

{document.page_content}
"""
            )

        return "\n\n".join(sections)

    @staticmethod
    def _build_history(
        history: list[Message] | None,
    ) -> str:
        """
        Format recent conversation history.
        """

        if not history:
            return "No previous conversation."

        return "\n".join(
            f"{message.role.capitalize()}: {message.content}"
            for message in history
        )

    @staticmethod
    def build(
        question: str,
        documents: list[Document],
        history: list[Message] | None = None,
        summary: str = "",
    ) -> str:
        """
        Build the complete prompt.
        """

        context = PromptBuilder._build_context(documents)

        conversation = PromptBuilder._build_history(history)

        if not summary:
            summary = "No previous summary."

        prompt = f"""
You are an enterprise AI assistant.

Your job is to answer questions using ONLY the retrieved document context.

Rules:

1. Use the retrieved context as the primary source of truth.
2. You may use the conversation summary and recent conversation
   to understand references like:
      - "it"
      - "that"
      - "the previous answer"
3. Never invent facts.
4. If the answer cannot be found in the retrieved context,
   respond exactly with:

I couldn't find the answer in the provided documents.

5. If the user asks for a simpler explanation,
   rewrite the retrieved information in easier language.
6. Keep responses concise unless the user requests details.

==================================================
Conversation Summary
==================================================

{summary}

==================================================
Recent Conversation
==================================================

{conversation}

==================================================
Retrieved Context
==================================================

{context}

==================================================
Current Question
==================================================

{question}

==================================================
Answer
==================================================
"""

        return prompt.strip()