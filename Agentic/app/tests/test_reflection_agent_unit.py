from unittest.mock import MagicMock, patch
from app.agents.reflection_agent import ReflectionAgent


def test_reflection_agent_fallback():
    agent = ReflectionAgent()
    empty_ans = agent.reflect("question", "")
    assert empty_ans == ""


@patch("app.agents.reflection_agent.llm")
def test_reflection_agent_reflect(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "Improved clear answer."
    mock_llm.invoke.return_value = mock_response

    agent = ReflectionAgent()
    result = agent.reflect("What is RAG?", "RAG is retrieval augmented generation.")
    assert result == "Improved clear answer."
