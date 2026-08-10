from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes import GraphNodes
from app.graph.edges import should_reflect, after_reflection


nodes = GraphNodes()

workflow = StateGraph(GraphState)

workflow.add_node("load_session", nodes.load_session)
workflow.add_node("intent", nodes.classify_intent)
workflow.add_node("agent", nodes.agent_node)
workflow.add_node("reflection", nodes.reflection_node)

workflow.set_entry_point("load_session")

workflow.add_edge("load_session", "intent")
workflow.add_edge("intent", "agent")

workflow.add_conditional_edges(
    "agent",
    should_reflect,
    {
        "reflection": "reflection",
        "end": END,
    },
)

# After reflection, either loop back to agent with a refined query or end.
workflow.add_conditional_edges(
    "reflection",
    after_reflection,
    {
        "agent": "agent",
        "end": END,
    },
)

graph = workflow.compile()
