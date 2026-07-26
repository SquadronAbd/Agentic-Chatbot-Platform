from app.memory.memory_service import MemoryService
from app.memory.conversation import ConversationMemory


class MemoryTool:
    """
    Tool for querying and interacting with conversation memory.
    """

    def __init__(self):
        self.memory_service = MemoryService()

    def get_history(self, memory: ConversationMemory):
        """
        Retrieves the raw conversation history messages.
        """
        if memory is None:
            return []
        return memory.get_history()

    def get_summary(self, memory: ConversationMemory) -> str:
        """
        Retrieves the summary of the conversation.
        """
        if memory is None:
            return ""
        return memory.get_summary()

    def answer_from_memory(self, question: str, memory: ConversationMemory) -> str:
        """
        Answers a user question based strictly on conversation memory.
        """
        if memory is None:
            return "No active session memory available."
        return self.memory_service.answer(question=question, memory=memory)
