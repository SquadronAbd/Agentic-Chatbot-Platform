from __future__ import annotations

from loguru import logger

from app.models.llm import llm


_STEP_BACK_PROMPT = """You are an expert at query transformation for financial document retrieval.

Given a specific financial question, generate a broader, more abstract version \
that retrieves relevant background context from financial reports alongside the specific answer.

Rules:
- One sentence only
- Broaden scope while staying financially relevant
- If the question is already broad or conceptual, return it unchanged

Examples:
Q: What was Apple's net income in Q3 2024?
A: What are Apple's profitability metrics and income trends across recent quarters?

Q: Did EBITDA margins improve year-over-year?
A: What are the EBITDA margin trends and operational efficiency metrics over recent periods?

Q: What is the current ratio for fiscal year 2023?
A: What are the liquidity ratios and short-term solvency metrics on the balance sheet?

Q: How much did operating expenses increase?
A: What are the operating expense components and their trends across reporting periods?

Original question: {query}
Step-back question:"""


class StepBackTransformer:
    """
    Generates an abstracted step-back query from the user's specific question.

    The step-back query is used alongside the original to retrieve broader
    context sections (e.g. the full Income Statement section) in addition to
    the specific data point the user is asking about.

    Falls back to the original query on any LLM failure so retrieval is
    never blocked.
    """

    def transform(self, query: str) -> str:
        try:
            prompt = _STEP_BACK_PROMPT.format(query=query)
            response = llm.invoke(prompt)
            content = getattr(response, "content", response)

            if isinstance(content, list):
                content = " ".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                ).strip()

            abstract = str(content).strip()
            return abstract if abstract else query

        except Exception as exc:
            logger.warning(f"Step-back transformation failed, using original query: {exc}")
            return query


transformer = StepBackTransformer()
