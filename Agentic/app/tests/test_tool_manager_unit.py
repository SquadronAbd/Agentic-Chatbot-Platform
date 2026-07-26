import pytest
from app.tools.tool_manager import ToolManager
from app.tools.memory_tool import MemoryTool
from app.memory.conversation import ConversationMemory


def test_tool_manager_registration():
    tm = ToolManager()
    tools = tm.list_tools()
    assert "retriever" in tools
    assert "memory" in tools
    assert "calculator" in tools
    assert "datetime" in tools
    assert "sql" in tools

    assert tm.get_tool("calculator") is not None


def test_memory_tool():
    mem_tool = MemoryTool()
    mem = ConversationMemory()
    mem.add_user_message("Hello")
    mem.add_ai_message("Hi there")
    mem.set_summary("User greeted AI.")

    history = mem_tool.get_history(mem)
    summary = mem_tool.get_summary(mem)

    assert len(history) == 2
    assert summary == "User greeted AI."
