from app.graph.state import GraphState

state: GraphState = {
    "session_id": "abdullah",
    "question": "What is RAG?",
    "intent": "",
    "documents": [],
    "answer": "",
    "summary": "",
    "sources": [],
}

print("=" * 60)
print("GRAPH STATE")
print("=" * 60)

for key, value in state.items():
    print(f"{key}: {value}")