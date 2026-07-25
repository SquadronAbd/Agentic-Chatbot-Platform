from typing import TypedDict, Any, List, Dict, Optional
from langchain_core.documents import Document


class GraphState(TypedDict, total=False):
    """
    Shared state used across every LangGraph node.
    """

    session_id: str
    question: str
    agent: str
    intent: str  # Alias for backward compatibility
    retrieved_documents: List[Document]
    documents: List[Document]  # Alias for backward compatibility
    conversation_history: List[Any]
    summary: str
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    # Conversation Memory
    memory: Any