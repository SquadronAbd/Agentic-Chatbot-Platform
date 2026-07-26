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
                [f"[{doc.metadata.get('source', 'source')}]\n{doc.page_content}" for doc in documents]
            )

        prompt = f"""
You are an expert Reflection Agent. Your job is to review and improve an AI-generated answer about financial reports.

CRITICAL INSTRUCTIONS:
1. Verify correctness and logical coherence against the retrieved context.
2. Improve clarity and readability — make the answer direct and confident.
3. Remove any unsupported claims or hallucinations.
4. NEVER use "Document 1", "Document 2", or any numeric document labels in the output.
5. NEVER add meta-commentary like "Note: The original source citations are intact" or "The answer has been polished".
6. Just return the improved answer text directly — no preamble, no footnotes.
7. If the draft answer is already concise and accurate, return it with minimal changes.

Original Question:
{question}

Retrieved Context:
{doc_context if doc_context else "None"}

Draft Answer:
{answer}

Improved Answer:
"""
        response = llm.invoke(prompt)
        improved = self._extract_text(response)

        return improved if improved else answer
