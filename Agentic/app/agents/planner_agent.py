from typing import Any, Dict, Optional
from app.models.llm import llm
from app.agents.document_agent import DocumentAgent
from app.agents.general_agent import GeneralAgent
from app.tools.tool_manager import ToolManager


class PlannerAgent:
    """
    Handles complex multi-step questions by retrieving context then
    planning and synthesising in a single LLM call.
    """

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        document_agent: Optional[DocumentAgent] = None,
        general_agent: Optional[GeneralAgent] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.document_agent = document_agent or DocumentAgent(self.tool_manager)
        self.general_agent = general_agent or GeneralAgent(self.tool_manager)

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        return str(content)

    async def plan_and_execute(
        self,
        question: str,
        memory=None,
        source_filter: tuple[str, ...] | None = None,
        owner_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Retrieves document context then synthesises a structured answer in one
        combined prompt — eliminates the separate plan-generation LLM call.
        """
        # Step 1: Retrieve relevant documents (async — document_agent handles thread offload)
        doc_res = await self.document_agent.answer(
            question=question, memory=memory, source_filter=source_filter, owner_id=owner_id
        )
        retrieved_docs = doc_res.get("documents", [])
        sources = doc_res.get("sources", [])
        doc_context = doc_res.get("answer", "")

        # Step 2: Plan + synthesise in a single async LLM call
        prompt = f"""You are a strategic financial analyst.

Question: {question}

Retrieved Context:
{doc_context}

First, briefly outline 2-4 reasoning steps you will follow, then provide a
comprehensive, clearly structured answer that addresses all parts of the question.
Use specific figures and citations from the context where available."""

        final_response = await llm.ainvoke(prompt)
        final_answer = self._extract_text(final_response)

        return {
            "answer": final_answer,
            "plan": "",
            "documents": retrieved_docs,
            "sources": sources,
        }
