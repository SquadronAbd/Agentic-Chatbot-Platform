from typing import Any, Dict

from app.graph.workflow import graph
from app.memory.session import session_manager
from app.memory.summarizer import ConversationSummarizer


class RAGService:

    def __init__(
        self,
        summary_threshold: int = 20,
        recent_messages: int = 6,
    ):
        self.session_manager = session_manager  # shared singleton
        self.summarizer = ConversationSummarizer()
        self.summary_threshold = summary_threshold
        self.recent_messages = recent_messages

    def _summarize_if_needed(self, memory) -> None:
        if memory.message_count() < self.summary_threshold:
            return
        summary = self.summarizer.summarize(memory.get_history())
        recent = memory.last_messages(self.recent_messages)
        memory.replace_history(summary=summary, recent_messages=recent)

    def ask(self, session_id: str, question: str) -> Dict[str, Any]:
        try:
            memory = self.session_manager.get_memory(session_id)
            self._summarize_if_needed(memory)

            initial_state = {
                "session_id": session_id,
                "question": question,
                "agent": "",
                "intent": "",
                "retrieved_documents": [],
                "documents": [],
                "conversation_history": memory.get_history(),
                "summary": memory.get_summary(),
                "answer": "",
                "sources": [],
                "metadata": {},
                "memory": memory,
            }

            result = graph.invoke(initial_state)

            answer = result.get("answer", "")
            documents = result.get("retrieved_documents", result.get("documents", []))
            sources = result.get("sources", [])

            formatted_sources = []
            for item in sources:
                if isinstance(item, dict):
                    formatted_sources.append(item)
                elif hasattr(item, "metadata"):
                    formatted_sources.append({
                        "source": item.metadata.get("source", "Unknown"),
                        "metadata": item.metadata,
                        "content": getattr(item, "page_content", ""),
                    })

            if answer:
                memory.add_user_message(question)
                memory.add_ai_message(answer)

            return {
                "success": True,
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "summary": memory.get_summary(),
                "messages": memory.message_count(),
                "documents_retrieved": len(documents),
                "sources": formatted_sources,
            }

        except Exception as e:
            return {
                "success": False,
                "session_id": session_id,
                "question": question,
                "answer": "",
                "summary": "",
                "messages": 0,
                "documents_retrieved": 0,
                "sources": [],
                "error": str(e),
            }
