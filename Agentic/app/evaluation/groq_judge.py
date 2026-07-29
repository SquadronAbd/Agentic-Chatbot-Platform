from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from deepeval.models import DeepEvalBaseLLM


class GroqJudge(DeepEvalBaseLLM):
    """DeepEval-compatible LLM judge backed by Groq."""

    def __init__(self, model: str, api_key: str) -> None:
        self._model_name = model
        self._client = ChatGroq(model=model, api_key=api_key, temperature=0)

    def load_model(self):
        return self._client

    def generate(self, prompt: str) -> str:
        response = self._client.invoke([HumanMessage(content=prompt)])
        return response.content  # type: ignore[return-value]

    async def a_generate(self, prompt: str) -> str:
        response = await self._client.ainvoke([HumanMessage(content=prompt)])
        return response.content  # type: ignore[return-value]

    def get_model_name(self) -> str:
        return self._model_name
