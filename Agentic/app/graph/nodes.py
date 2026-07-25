from app.graph.state import GraphState
from app.memory.session import session_manager
from app.router.intent_classifier import IntentClassifier
from app.agents.agent_manager import AgentManager
from app.tools.tool_manager import ToolManager


# Module-level singletons — constructed once, shared across all requests
_tool_manager = ToolManager()
_agent_manager = AgentManager(_tool_manager)
_intent_classifier = IntentClassifier()

_PLANNER_KEYWORDS = ["compare", "difference between", "step by step", "break down"]


class GraphNodes:

    def __init__(self):
        self.session_manager = session_manager
        self.intent_classifier = _intent_classifier
        self.agent_manager = _agent_manager

    # 1. LOAD SESSION
    def load_session(self, state: GraphState) -> GraphState:
        session_id = state.get("session_id", "default")
        memory = self.session_manager.get_memory(session_id)

        # Always use the singleton's memory object so history is preserved
        # across the RAGService → graph boundary
        state["memory"] = memory
        state["conversation_history"] = memory.get_history()
        state["summary"] = memory.get_summary()
        state.setdefault("metadata", {})

        return state

    # 2. INTENT CLASSIFICATION
    def classify_intent(self, state: GraphState) -> GraphState:
        question = state.get("question", "")

        if any(kw in question.lower() for kw in _PLANNER_KEYWORDS):
            intent = "planner"
        else:
            intent = self.intent_classifier.classify(question).value

        state["intent"] = intent
        state["agent"] = intent
        return state

    # 3-6. AGENT EXECUTION (all intents flow through AgentManager.ask)
    def _execute(self, state: GraphState) -> GraphState:
        result = self.agent_manager.ask(
            question=state.get("question", ""),
            memory=state.get("memory"),
            intent=state.get("intent", "general"),
            use_reflection=False,  # graph's reflection node handles this
        )
        state["answer"] = result["answer"]
        state["retrieved_documents"] = result.get("documents", [])
        state["documents"] = result.get("documents", [])
        state["sources"] = result.get("sources", [])
        if result.get("plan"):
            state.setdefault("metadata", {})["plan"] = result["plan"]
        return state

    def planner_node(self, state: GraphState) -> GraphState:
        return self._execute(state)

    def retrieve_node(self, state: GraphState) -> GraphState:
        return self._execute(state)

    def memory_node(self, state: GraphState) -> GraphState:
        return self._execute(state)

    def general_node(self, state: GraphState) -> GraphState:
        return self._execute(state)

    # 7. REFLECTION
    def reflection_node(self, state: GraphState) -> GraphState:
        draft = state.get("answer", "")
        if draft:
            state["answer"] = self.agent_manager.reflection.reflect(
                question=state.get("question", ""),
                answer=draft,
                documents=state.get("retrieved_documents", []),
            )
        return state
