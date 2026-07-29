from app.memory.conversation import ConversationMemory


class MemoryService:

    def answer(
        self,
        question: str,
        memory: ConversationMemory,
    ) -> str:

        question = question.lower()

        _SENTINEL = "I couldn't answer from conversation memory."

        if "summary" in question:
            if memory.get_summary():
                return memory.get_summary()
            # No summary yet — let the LLM summarise from history
            return _SENTINEL

        if "who are we talking about" in question:
            if memory.get_summary():
                return memory.get_summary()
            # No summary to extract a subject from — let the LLM answer
            return _SENTINEL

        if "what did i ask" in question:
            # Too fragile to guess with users[-1] — let the LLM search history
            return _SENTINEL

        return _SENTINEL