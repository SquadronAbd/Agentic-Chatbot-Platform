from typing import Any, Optional

from app.models.llm import llm
from app.tools.tool_manager import ToolManager


class MemoryAgent:
    """
    Answers questions using conversation memory via ToolManager.
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.memory_tool = self.tool_manager.memory

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content.strip()

        return str(content)

    def answer(
        self,
        question: str,
        memory,
    ) -> str:
        if memory is not None:
            tool_ans = self.memory_tool.answer_from_memory(question, memory)
            if tool_ans and tool_ans != "I couldn't answer from conversation memory.":
                return tool_ans

        history = "" if memory is None else self.memory_tool.get_history(memory)
        summary = "" if memory is None else self.memory_tool.get_summary(memory)

        prompt = f"""
You are answering ONLY from the conversation history.

Conversation

{history}

Summary

{summary}

Question

{question}

Answer:
"""

        response = llm.invoke(prompt)

        return self._extract_text(response)