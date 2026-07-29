from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes import GraphNodes
from app.graph.router import route_intent
from app.graph.edges import should_reflect


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

workflow.add_edge("reflection", END)

graph = workflow.compile()
