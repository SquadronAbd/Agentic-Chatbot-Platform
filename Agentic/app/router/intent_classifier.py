import re
from enum import Enum
from typing import Any

from app.models.llm import llm


class QueryType(str, Enum):
    MEMORY = "memory"
    DOCUMENT = "document"
    GENERAL = "general"


# Fast rule-based patterns — checked before any LLM call.
_MEMORY_RE = re.compile(
    r"\b(what did (i|you) (ask|say|tell|mean)|previous(ly)?|earlier|last time"
    r"|summarize our|our conversation|you (said|told|answered)|remind me what"
    r"|what was (my|your|the) (question|answer|last))\b",
    re.I,
)

_DOCUMENT_RE = re.compile(
    r"\b(revenue|ebitda|profit|loss|margin|balance sheet|cash flow|earnings"
    r"|quarter|fiscal|fy\s*\d{2,4}|q[1-4]\s*\d{4}|annual report|10-k|10-q"
    r"|filing|sec|dividend|eps|net income|gross profit|operating income"
    r"|debt|equity|asset|liability|shareholder|stock|ticker|ipo|acquisition"
    r"|merger|financial (statement|result|performance|data|metric)"
    r"|what (is|are|was|were) (the )?(company|firm)'s"
    r"|\$[\d,.]+|[\d.]+\s*%)\b",
    re.I,
)


class IntentClassifier:
    """
    Classifies user intent into memory | document | general.

    Fast path: regex patterns cover ~80% of queries with no LLM call.
    Slow path: LLM used only for ambiguous queries the rules can't resolve.
    """

    def _extract_text(self, response: Any) -> str:
        content = response.content
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            texts = [p.get("text") for p in content if isinstance(p, dict) and p.get("text")]
            return "\n".join(texts).strip()
        return str(content)

    async def classify(self, question: str) -> QueryType:
        # Rule-based fast path — no LLM call needed for ~80% of queries
        if _MEMORY_RE.search(question):
            return QueryType.MEMORY
        if _DOCUMENT_RE.search(question):
            return QueryType.DOCUMENT

        # LLM fallback for ambiguous queries
        prompt = f"""You are an intent classifier. Classify the question into exactly one category.

memory   — questions about this conversation's history or previous answers
document — questions requiring retrieved financial documents or data
general  — greetings, coding, math, creative writing, anything else

Return ONLY ONE WORD (memory / document / general).

Question: {question}"""

        response = await llm.ainvoke(prompt)
        result = self._extract_text(response).lower().strip()

        if result == "memory":
            return QueryType.MEMORY
        if result == "document":
            return QueryType.DOCUMENT
        return QueryType.GENERAL