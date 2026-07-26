from app.graph.state import GraphState


def should_reflect(state: GraphState) -> str:
    """
    Determines whether to route through the Reflection node before finishing.
    """
    if state.get("answer"):
        return "reflection"
    return "end"
