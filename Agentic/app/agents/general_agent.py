import re
from typing import Any, Optional

from app.models.llm import llm
from app.tools.tool_manager import ToolManager


class GeneralAgent:
    """
    Handles general knowledge questions, leveraging calculation and datetime tools when needed.
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.calculator_tool = self.tool_manager.calculator
        self.datetime_tool = self.tool_manager.datetime

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content.strip()

        return str(content)

    def answer(
        self,
        question: str,
    ) -> str:
        q_lower = question.lower().strip()

        # Check for calculation trigger
        if "calculate" in q_lower or "math" in q_lower or re.search(r"^\d+[\s\+\-\*\/\%\*\*0-9\(\)]+$", q_lower):
            expr = re.sub(r"[^\d\+\-\*\/\%\(\)\.\,\s]", "", question).strip()
            if expr:
                calc_res = self.calculator_tool.calculate(expr)
                if calc_res.get("success"):
                    return f"Calculation Result: {calc_res['result']}"

        # Check for time/date trigger
        if any(term in q_lower for term in ["current time", "what time is it", "today's date", "current date"]):
            dt_info = self.datetime_tool.now()
            return f"Current Date & Time: {dt_info['date']} {dt_info['time']}"

        response = llm.invoke(question)

        return self._extract_text(response)