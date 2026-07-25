from unittest.mock import MagicMock, patch
from app.agents.planner_agent import PlannerAgent


@patch("app.agents.planner_agent.llm")
def test_planner_agent_plan_and_execute(mock_llm):
    mock_response = MagicMock()
    mock_response.content = "1. Retrieve docs\n2. Synthesize comparison"
    mock_llm.invoke.return_value = mock_response

    mock_doc_agent = MagicMock()
    mock_doc_agent.answer.return_value = {
        "answer": "Draft comparison context",
        "documents": [],
        "sources": [],
    }

    planner = PlannerAgent(document_agent=mock_doc_agent)
    res = planner.plan_and_execute("Compare 2020 and 2022 revenue")

    assert "answer" in res
    assert "plan" in res
