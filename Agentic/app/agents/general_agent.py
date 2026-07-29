import re
from typing import Any, Optional

from app.models.llm import llm
from app.tools.tool_manager import ToolManager


class GeneralAgent:
    """
    Handles general knowledge questions, memory recall, calculator, and datetime.
    Folds in MemoryAgent logic — memory questions are answered from session history
    before falling back to the LLM.
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.calculator_tool = self.tool_manager.calculator
        self.datetime_tool = self.tool_manager.datetime
        self.memory_tool = self.tool_manager.memory

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content.strip()
        return str(content)

    def answer(self, question: str, memory=None) -> str:
        q_lower = question.lower().strip()

        # Memory recall — try rule-based history lookup first
        if memory is not None:
            tool_ans = self.memory_tool.answer_from_memory(question, memory)
            if tool_ans and tool_ans != "I couldn't answer from conversation memory.":
                return tool_ans

        # Calculator
        if "calculate" in q_lower or "math" in q_lower or re.search(r"^\d+[\s\+\-\*\/\%\*\*0-9\(\)]+$", q_lower):
            expr = re.sub(r"[^\d\+\-\*\/\%\(\)\.\,\s]", "", question).strip()
            if expr:
                calc_res = self.calculator_tool.calculate(expr)
                if calc_res.get("success"):
                    return f"Calculation Result: {calc_res['result']}"

        # Date/time
        if any(term in q_lower for term in ["current time", "what time is it", "today's date", "current date"]):
            dt_info = self.datetime_tool.now()
            return f"Current Date & Time: {dt_info['date']} {dt_info['time']}"

        # If memory context available, include history in the LLM prompt
        if memory is not None:
            history = self.memory_tool.get_history(memory)
            summary = self.memory_tool.get_summary(memory)
            if history or summary:
                prompt = f"""You are a helpful assistant. Answer using the conversation context below if relevant.

Conversation Summary:
{summary}

Recent Conversation:
{history}

Question: {question}

Answer:"""
                response = llm.invoke(prompt)
                return self._extract_text(response)

        response = llm.invoke(question)
        return self._extract_text(response)
