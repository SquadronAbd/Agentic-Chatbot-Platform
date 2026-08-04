from typing import Any, Dict

from app.graph.workflow import graph
from app.memory.session import session_manager
from app.memory.summarizer import ConversationSummarizer
from app.rag.doc_store import get_sources


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

    async def _summarize_if_needed(self, memory) -> None:
        if memory.message_count() < self.summary_threshold:
            return
        summary = await self.summarizer.summarize(memory.get_history())
        recent = memory.last_messages(self.recent_messages)
        memory.replace_history(summary=summary, recent_messages=recent)

    async def ask(self, session_id: str, question: str, owner_id: str | None = None) -> Dict[str, Any]:
        try:
            memory = self.session_manager.get_memory(session_id)
            await self._summarize_if_needed(memory)

            # session_id format: "{user_id}_{conversation_id}" — extract user_id
            # to look up which documents this user has uploaded.
            owner_id = owner_id or (session_id.split("_", 1)[0] if "_" in session_id else session_id)
            source_filter = get_sources(owner_id)

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
                "source_filter": source_filter,
                "owner_id": owner_id,
            }

            result = await graph.ainvoke(initial_state)

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
                # Persist updated memory back to Redis
                self.session_manager.save_memory(session_id, memory)

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
