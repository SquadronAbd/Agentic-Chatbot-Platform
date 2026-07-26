from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.graph.nodes import GraphNodes
from app.graph.router import route_intent
from app.graph.edges import should_reflect


nodes = GraphNodes()

workflow = StateGraph(GraphState)

# --------------------------------------------------
# Nodes
# --------------------------------------------------

workflow.add_node("load_session", nodes.load_session)
workflow.add_node("intent", nodes.classify_intent)
workflow.add_node("planner", nodes.planner_node)
workflow.add_node("retrieve", nodes.retrieve_node)
workflow.add_node("memory", nodes.memory_node)
workflow.add_node("general", nodes.general_node)
workflow.add_node("reflection", nodes.reflection_node)

# --------------------------------------------------
# Entry Point
# --------------------------------------------------

workflow.set_entry_point("load_session")

# --------------------------------------------------
# Flow
# --------------------------------------------------

workflow.add_edge("load_session", "intent")

workflow.add_conditional_edges(
    "intent",
    route_intent,
    {
        "planner": "planner",
        "document": "retrieve",
        "memory": "memory",
        "general": "general",
    },
)

workflow.add_conditional_edges(
    "planner",
    should_reflect,
    {
        "reflection": "reflection",
        "end": END,
    },
)

workflow.add_conditional_edges(
    "retrieve",
    should_reflect,
    {
        "reflection": "reflection",
        "end": END,
    },
)

workflow.add_conditional_edges(
    "memory",
    should_reflect,
    {
        "reflection": "reflection",
        "end": END,
    },
)

workflow.add_conditional_edges(
    "general",
    should_reflect,
    {
        "reflection": "reflection",
        "end": END,
    },
)

workflow.add_edge("reflection", END)

graph = workflow.compile()