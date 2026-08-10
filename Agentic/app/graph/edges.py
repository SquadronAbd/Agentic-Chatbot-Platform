from app.graph.state import GraphState


def should_reflect(state: GraphState) -> str:
    """
    Only reflect when documents were retrieved and intent warrants it.
    Skips reflection for general/memory queries to save an LLM call.
    """
    has_docs = bool(state.get("retrieved_documents"))
    intent = state.get("intent", "general")
    if state.get("answer") and has_docs and intent in ("document", "planner"):
        return "reflection"
    return "end"


def after_reflection(state: GraphState) -> str:
    """
    After reflection, loop back to the agent if the answer was insufficient
    and a refined query was produced. Otherwise end.
    """
    if state.get("refined_query"):
        return "agent"
    return "end"
