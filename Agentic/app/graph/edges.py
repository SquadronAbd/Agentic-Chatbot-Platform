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
