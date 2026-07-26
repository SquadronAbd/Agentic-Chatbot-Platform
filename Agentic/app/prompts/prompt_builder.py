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

        for document in documents:
            source = document.metadata.get("source", "Unknown")
            header = document.metadata.get("h1") or document.metadata.get("h2") or ""
            label = f"{source}" + (f" — {header}" if header else "")

            sections.append(
                f"""[{label}]
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
You are an enterprise AI assistant specialising in financial report analysis.

Your job is to answer questions using ONLY the retrieved document context provided below.

Rules:

1. Answer directly and confidently — do not say "Document 1 says" or "According to Document 2". Just state the facts.
2. You may reference the source file name naturally if it helps (e.g. "In the 2022 Annual Report..."), but never use numeric document labels like "Document 1".
3. Use the conversation summary and recent conversation to understand references like "it", "that", or "the previous answer".
4. Never invent facts or figures not present in the context.
5. If the answer cannot be found in the retrieved context, respond exactly with:

I couldn't find the answer in the provided documents.

6. Keep responses concise and direct unless the user requests details.
7. When citing numbers, percentages, or financial figures, include them exactly as they appear in the source.

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