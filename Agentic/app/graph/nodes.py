from typing import Dict, Any
from app.graph.state import GraphState
from app.memory.session import SessionManager
from app.router.intent_classifier import IntentClassifier
from app.agents.agent_manager import AgentManager
from app.agents.reflection_agent import ReflectionAgent
from app.agents.planner_agent import PlannerAgent
from app.tools.tool_manager import ToolManager


class GraphNodes:
    def __init__(self):
        self.session_manager = SessionManager()
        self.intent_classifier = IntentClassifier()
        self.tool_manager = ToolManager()
        self.agent_manager = AgentManager(self.tool_manager)
        self.reflection_agent = ReflectionAgent()
        self.planner_agent = PlannerAgent(self.tool_manager)

    # 1. LOAD SESSION
    def load_session(self, state: GraphState) -> GraphState:
        session_id = state.get("session_id", "default")
        memory = self.session_manager.get_memory(session_id)

        state["memory"] = memory
        state["conversation_history"] = memory.get_history() if memory else []
        state["summary"] = memory.get_summary() if memory else ""
        if "metadata" not in state:
            state["metadata"] = {}

        return state

    # 2. ROUTER NODE
    def classify_intent(self, state: GraphState) -> GraphState:
        question = state.get("question", "")
        # Check if query needs multi-step planning
        if any(kw in question.lower() for kw in ["compare", "difference between", "step by step", "break down"]):
            state["agent"] = "planner"
            state["intent"] = "planner"
        else:
            intent = self.intent_classifier.classify(question)
            state["agent"] = intent.value
            state["intent"] = intent.value

        return state

    # 3. PLANNER NODE
    def planner_node(self, state: GraphState) -> GraphState:
        res = self.planner_agent.plan_and_execute(
            question=state.get("question", ""),
            memory=state.get("memory"),
        )
        state["answer"] = res["answer"]
        state["retrieved_documents"] = res.get("documents", [])
        state["documents"] = res.get("documents", [])
        state["sources"] = res.get("sources", [])
        state["metadata"]["plan"] = res.get("plan", "")
        return state

    # 4. DOCUMENT NODE / RETRIEVER NODE
    def retrieve_node(self, state: GraphState) -> GraphState:
        doc_res = self.agent_manager.document.answer(
            question=state.get("question", ""),
            memory=state.get("memory"),
        )
        state["answer"] = doc_res["answer"]
        state["retrieved_documents"] = doc_res.get("documents", [])
        state["documents"] = doc_res.get("documents", [])
        state["sources"] = doc_res.get("sources", [])
        return state

    # 5. MEMORY NODE
    def memory_node(self, state: GraphState) -> GraphState:
        answer = self.agent_manager.memory.answer(
            question=state.get("question", ""),
            memory=state.get("memory"),
        )
        state["answer"] = answer
        state["retrieved_documents"] = []
        state["documents"] = []
        state["sources"] = []
        return state

    # 6. GENERAL CHAT NODE
    def general_node(self, state: GraphState) -> GraphState:
        answer = self.agent_manager.general.answer(
            question=state.get("question", "")
        )
        state["answer"] = answer
        state["retrieved_documents"] = []
        state["documents"] = []
        state["sources"] = []
        return state

    # 7. REFLECTION NODE
    def reflection_node(self, state: GraphState) -> GraphState:
        draft = state.get("answer", "")
        if draft:
            improved = self.reflection_agent.reflect(
                question=state.get("question", ""),
                answer=draft,
                documents=state.get("retrieved_documents", state.get("documents", [])),
            )
            state["answer"] = improved
        return state