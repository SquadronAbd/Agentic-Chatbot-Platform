from app.graph.state import GraphState
from app.memory.session import session_manager
from app.router.intent_classifier import IntentClassifier
from app.agents.agent_manager import AgentManager
from app.agents.reflection_agent import ReflectionAgent
from app.tools.tool_manager import ToolManager


_tool_manager = ToolManager()
_agent_manager = AgentManager(_tool_manager)
_intent_classifier = IntentClassifier()

_PLANNER_KEYWORDS = ["compare", "difference between", "step by step", "break down"]


class GraphNodes:

    def __init__(self):
        self.session_manager = session_manager
        self.intent_classifier = _intent_classifier
        self.agent_manager = _agent_manager

    def load_session(self, state: GraphState) -> GraphState:
        session_id = state.get("session_id", "default")
        memory = self.session_manager.get_memory(session_id)
        state["memory"] = memory
        state["conversation_history"] = memory.get_history()
        state["summary"] = memory.get_summary()
        state.setdefault("metadata", {})
        state.setdefault("retry_count", 0)
        return state

    async def classify_intent(self, state: GraphState) -> GraphState:
        question = state.get("question", "")
        if any(kw in question.lower() for kw in _PLANNER_KEYWORDS):
            intent = "planner"
        else:
            intent = (await self.intent_classifier.classify(question)).value
        state["intent"] = intent
        state["agent"] = intent
        return state

    async def agent_node(self, state: GraphState) -> GraphState:
        question = state.get("refined_query") or state.get("question", "")
        source_filter_list = state.get("source_filter") or []
        result = await self.agent_manager.ask(
            question=question,
            memory=state.get("memory"),
            intent=state.get("intent", "general"),
            source_filter=tuple(source_filter_list) if source_filter_list else None,
            owner_id=state.get("owner_id"),
        )
        state["answer"] = result["answer"]
        state["retrieved_documents"] = result.get("documents", [])
        state["documents"] = result.get("documents", [])
        state["sources"] = result.get("sources", [])
        if result.get("plan"):
            state.setdefault("metadata", {})["plan"] = result["plan"]
        return state

    async def reflection_node(self, state: GraphState) -> GraphState:
        draft = state.get("answer", "")
        if not draft:
            return state

        retry_count = state.get("retry_count", 0)
        can_retry = retry_count < ReflectionAgent.MAX_RETRIES

        if can_retry and state.get("intent") in ("document", "planner"):
            result = await self.agent_manager.reflection.reflect_with_sufficiency(
                question=state.get("question", ""),
                answer=draft,
                documents=state.get("retrieved_documents", []),
            )
            state["answer"] = result["answer"]

            if not result["sufficient"] and result.get("refined_query"):
                state["refined_query"] = result["refined_query"]
                state["retry_count"] = retry_count + 1
            else:
                state["refined_query"] = None
        else:
            state["answer"] = await self.agent_manager.reflection.reflect(
                question=state.get("question", ""),
                answer=draft,
                documents=state.get("retrieved_documents", []),
            )
            state["refined_query"] = None

        return state
