from typing import Any, Dict, Optional

from app.agents.router_agent import RouterAgent
from app.agents.document_agent import DocumentAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.general_agent import GeneralAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.reflection_agent import ReflectionAgent
from app.tools.tool_manager import ToolManager


class AgentManager:
    """
    Unified entry point coordinating all system AI agents.
    """

    def __init__(
        self,
        tool_manager: Optional[ToolManager] = None,
    ):
        self.tool_manager = tool_manager or ToolManager()
        self.router = RouterAgent()
        self.document = DocumentAgent(self.tool_manager)
        self.memory = MemoryAgent(self.tool_manager)
        self.general = GeneralAgent(self.tool_manager)
        self.planner = PlannerAgent(self.tool_manager, self.document, self.general, self.memory)
        self.reflection = ReflectionAgent()

    def ask(
        self,
        question: str,
        memory: Optional[Any] = None,
        use_reflection: bool = True,
    ) -> Dict[str, Any]:
        """
        Routes the question to the appropriate agent pipeline and optionally runs reflection.
        """
        route = self.router.route(question)
        documents = []
        sources = []

        # Complex query check for Planner
        if any(kw in question.lower() for kw in ["compare", "difference between", "step by step", "break down"]):
            plan_res = self.planner.plan_and_execute(question, memory)
            draft_answer = plan_res["answer"]
            documents = plan_res.get("documents", [])
            sources = plan_res.get("sources", [])
        elif route == "document":
            doc_res = self.document.answer(question=question, memory=memory)
            draft_answer = doc_res["answer"]
            documents = doc_res.get("documents", [])
            sources = doc_res.get("sources", [])
        elif route == "memory":
            draft_answer = self.memory.answer(question, memory)
        else:
            draft_answer = self.general.answer(question)

        # Reflection step
        if use_reflection and draft_answer:
            final_answer = self.reflection.reflect(
                question=question,
                answer=draft_answer,
                documents=documents,
            )
        else:
            final_answer = draft_answer

        return {
            "answer": final_answer,
            "sources": sources,
            "documents": documents,
            "route": route,
        }