from typing import Any, Dict, Optional

from app.agents.document_agent import DocumentAgent
from app.agents.general_agent import GeneralAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.reflection_agent import ReflectionAgent
from app.agents.router_agent import RouterAgent
from app.tools.tool_manager import ToolManager


class AgentManager:
    """
    Single entry point for all agent execution.

    The graph's classify_intent node classifies the query and passes the
    intent via the `intent` parameter — no second LLM call for routing.
    When called standalone (outside the graph), classification is done here.
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
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
        intent: Optional[str] = None,
        use_reflection: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes the full agent pipeline for a given question.

        Args:
            question:       User's question.
            memory:         ConversationMemory for the current session.
            intent:         Pre-classified intent from the graph's classify_intent
                            node ('planner', 'document', 'memory', 'general').
                            When None, classification is done here via RouterAgent.
            use_reflection: Whether to run the ReflectionAgent on the draft answer.
                            Set to False when the graph's reflection node handles it.
        """
        # Classify only if the graph hasn't already done it
        if intent is None:
            intent = self.router.route(question)

        documents: list = []
        sources: list = []
        plan: str = ""

        if intent == "planner":
            result = self.planner.plan_and_execute(question, memory)
            draft_answer = result["answer"]
            documents = result.get("documents", [])
            sources = result.get("sources", [])
            plan = result.get("plan", "")

        elif intent == "document":
            result = self.document.answer(question=question, memory=memory)
            draft_answer = result["answer"]
            documents = result.get("documents", [])
            sources = result.get("sources", [])

        elif intent == "memory":
            draft_answer = self.memory.answer(question=question, memory=memory)

        else:
            draft_answer = self.general.answer(question=question)

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
            "documents": documents,
            "sources": sources,
            "intent": intent,
            "plan": plan,
        }
