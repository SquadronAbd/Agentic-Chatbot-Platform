from typing import Any, Dict, Optional

from app.agents.document_agent import DocumentAgent
from app.agents.general_agent import GeneralAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.reflection_agent import ReflectionAgent
from app.router.intent_classifier import IntentClassifier
from app.tools.tool_manager import ToolManager


class AgentManager:
    """
    Single entry point for all agent execution.

    Intent is pre-classified by the graph's classify_intent node (no second LLM
    call for routing). When called standalone (outside the graph), classification
    is done here via IntentClassifier.

    Memory and general queries both route to GeneralAgent — MemoryAgent has been
    folded in there. RouterAgent wrapper has been removed; IntentClassifier is
    called directly.
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self._classifier = IntentClassifier()
        self.document = DocumentAgent(self.tool_manager)
        self.general = GeneralAgent(self.tool_manager)
        self.planner = PlannerAgent(self.tool_manager, self.document, self.general)
        self.reflection = ReflectionAgent()

    async def ask(
        self,
        question: str,
        memory: Optional[Any] = None,
        intent: Optional[str] = None,
        use_reflection: bool = True,
        source_filter: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        if intent is None:
            intent = (await self._classifier.classify(question)).value

        documents: list = []
        sources: list = []

        if intent == "planner":
            result = await self.planner.plan_and_execute(question, memory)
            draft_answer = result["answer"]
            documents = result.get("documents", [])
            sources = result.get("sources", [])

        elif intent == "document":
            result = await self.document.answer(question=question, memory=memory, source_filter=source_filter)
            draft_answer = result["answer"]
            documents = result.get("documents", [])
            sources = result.get("sources", [])

        else:
            # Handles both "memory" and "general" intents
            draft_answer = await self.general.answer(question=question, memory=memory)

        if use_reflection and draft_answer and documents:
            final_answer = await self.reflection.reflect(
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
            "plan": "",
        }
