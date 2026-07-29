from app.graph.state import GraphState


def route_intent(state: GraphState) -> str:
    """
    Retained for backward compatibility with any external callers.
    The workflow no longer uses this — intent routes directly to agent_node.
    """
    agent = state.get("agent") or state.get("intent") or "general"
    if agent in ["planner", "document", "memory", "general"]:
        return agent
    return "general"
