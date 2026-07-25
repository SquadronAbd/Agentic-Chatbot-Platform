from typing import Any, List, Optional
from langchain_core.documents import Document
from app.models.llm import llm


class ReflectionAgent:
    """
    Critiques and improves generated responses.
    Verifies correctness, improves clarity, removes hallucinations, and preserves citations.
    """

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        return str(content)

    def reflect(
        self,
        question: str,
        answer: str,
        documents: Optional[List[Document]] = None,
    ) -> str:
        """
        Refines and improves the draft answer.
        """
        if not answer or not answer.strip():
            return answer

        doc_context = ""
        if documents:
            doc_context = "\n\n".join(
                [f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(documents)]
            )

        prompt = f"""
You are an expert Reflection Agent. Your job is to review and improve an AI generated answer.

CRITICAL INSTRUCTIONS:
1. Verify correctness and logical coherence.
2. Improve clarity and readability.
3. Remove any unsupported claims or hallucinations.
4. Keep all original source citations intact.
5. If the draft answer is already excellent, return it with minimal polishing.

Original Question:
{question}

Retrieved Context (if any):
{doc_context if doc_context else "None"}

Draft Answer:
{answer}

Improved Answer:
"""
        response = llm.invoke(prompt)
        improved = self._extract_text(response)

        return improved if improved else answer
