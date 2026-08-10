from typing import Any, List, Optional
from langchain_core.documents import Document
from app.models.llm import llm


class ReflectionAgent:
    """
    Critiques and improves generated responses.
    Verifies correctness, improves clarity, removes hallucinations, and preserves citations.
    Can flag an answer as insufficient and suggest a refined retrieval query.
    """

    MAX_RETRIES = 2

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        return str(content)

    async def reflect(
        self,
        question: str,
        answer: str,
        documents: Optional[List[Document]] = None,
    ) -> str:
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
        response = await llm.ainvoke(prompt)
        improved = self._extract_text(response)

        return improved if improved else answer

    async def reflect_with_sufficiency(
        self,
        question: str,
        answer: str,
        documents: Optional[List[Document]] = None,
    ) -> dict:
        """
        Reflects on the answer and judges whether it sufficiently addresses
        the question. If not, returns a refined query for re-retrieval.
        """
        if not answer or not answer.strip():
            return {"answer": answer, "sufficient": True, "refined_query": None}

        doc_context = ""
        if documents:
            doc_context = "\n\n".join(
                [f"[{doc.metadata.get('source', 'source')}]\n{doc.page_content}" for doc in documents]
            )

        prompt = f"""You are an expert Reflection Agent reviewing an AI-generated answer about financial reports.

Original Question:
{question}

Retrieved Context:
{doc_context if doc_context else "None"}

Draft Answer:
{answer}

Evaluate the draft answer against the question and context. Respond in EXACTLY this format:

SUFFICIENT: YES or NO
REFINED_QUERY: (only if SUFFICIENT is NO — write a better search query to retrieve the missing information; otherwise write NONE)
IMPROVED_ANSWER: (the improved answer text — clean, direct, no meta-commentary, no "Document 1/2" labels)
"""
        response = await llm.ainvoke(prompt)
        text = self._extract_text(response)

        sufficient = True
        refined_query = None
        improved_answer = answer

        lines = text.split("\n")
        answer_lines = []
        in_answer = False

        for line in lines:
            if line.strip().upper().startswith("SUFFICIENT:"):
                val = line.split(":", 1)[1].strip().upper()
                sufficient = val.startswith("YES")
            elif line.strip().upper().startswith("REFINED_QUERY:"):
                val = line.split(":", 1)[1].strip()
                if val.upper() != "NONE" and val:
                    refined_query = val
            elif line.strip().upper().startswith("IMPROVED_ANSWER:"):
                in_answer = True
                remainder = line.split(":", 1)[1].strip()
                if remainder:
                    answer_lines.append(remainder)
            elif in_answer:
                answer_lines.append(line)

        if answer_lines:
            improved_answer = "\n".join(answer_lines).strip()

        return {
            "answer": improved_answer if improved_answer else answer,
            "sufficient": sufficient,
            "refined_query": refined_query,
        }
