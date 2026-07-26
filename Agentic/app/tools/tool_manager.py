from typing import Any, Dict
from app.tools.retriever_tool import RetrieverTool
from app.tools.memory_tool import MemoryTool
from app.tools.calculator import CalculatorTool
from app.tools.datetime_tool import DateTimeTool
from app.tools.sql_tool import SQLTool


class ToolManager:
    """
    Central manager and registry for system tools.
    """

    def __init__(self):
        self.retriever = RetrieverTool()
        self.memory = MemoryTool()
        self.calculator = CalculatorTool()
        self.datetime = DateTimeTool()
        self.sql = SQLTool()

        self._tools: Dict[str, Any] = {
            "retriever": self.retriever,
            "memory": self.memory,
            "calculator": self.calculator,
            "datetime": self.datetime,
            "sql": self.sql,
        }

    def get_tool(self, name: str) -> Any:
        """
        Retrieves a tool instance by name.
        """
        return self._tools.get(name.lower())

    def list_tools(self) -> list[str]:
        """
        Returns all registered tool names.
        """
        return list(self._tools.keys())
