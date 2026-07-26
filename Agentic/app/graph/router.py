from app.graph.state import GraphState


def route_intent(state: GraphState) -> str:
    """
    Decide which agent node to execute after intent classification.
    """
    agent = state.get("agent") or state.get("intent") or "general"
    if agent in ["planner", "document", "memory", "general"]:
        return agent
    return "general"