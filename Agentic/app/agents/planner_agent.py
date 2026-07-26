from typing import Any, Dict, Optional
from app.models.llm import llm
from app.agents.document_agent import DocumentAgent
from app.agents.general_agent import GeneralAgent
from app.agents.memory_agent import MemoryAgent
from app.tools.tool_manager import ToolManager


class PlannerAgent:
    """
    Decomposes complex requests into subtasks and coordinates execution.
    """

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
        document_agent: Optional[DocumentAgent] = None,
        general_agent: Optional[GeneralAgent] = None,
        memory_agent: Optional[MemoryAgent] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.document_agent = document_agent or DocumentAgent(self.tool_manager)
        self.general_agent = general_agent or GeneralAgent(self.tool_manager)
        self.memory_agent = memory_agent or MemoryAgent(self.tool_manager)

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        return str(content)

    def plan_and_execute(
        self,
        question: str,
        memory=None,
    ) -> Dict[str, Any]:
        """
        Decomposes user question into plan steps and executes them.
        """
        # Step 1: Generate Plan
        plan_prompt = f"""
You are a strategic Planner Agent.
Break down the following complex request into 2-4 concise subtasks.

User Question: {question}

Format your output as a numbered list of action steps.
"""
        plan_response = llm.invoke(plan_prompt)
        plan_text = self._extract_text(plan_response)

        # Step 2: Retrieve document context for complex queries
        doc_res = self.document_agent.answer(question=question, memory=memory)
        retrieved_docs = doc_res.get("documents", [])
        sources = doc_res.get("sources", [])
        draft_answer = doc_res.get("answer", "")

        # Step 3: Synthesize final answer combining plan and document context
        synthesis_prompt = f"""
You are executing a multi-step analytical plan for the following question:

Question: {question}

Plan of Execution:
{plan_text}

Subtask Insights & Context:
{draft_answer}

Provide a comprehensive, clearly structured final answer addressing all parts of the user request.
"""
        final_response = llm.invoke(synthesis_prompt)
        final_answer = self._extract_text(final_response)

        return {
            "answer": final_answer,
            "plan": plan_text,
            "documents": retrieved_docs,
            "sources": sources,
        }
