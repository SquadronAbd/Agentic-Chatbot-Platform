"""
Eval-specific GroqJudge that uses the openai SDK pointed at Groq's
OpenAI-compatible endpoint.  No langchain-groq dependency required.
"""
from __future__ import annotations

from openai import AsyncOpenAI, OpenAI
from deepeval.models import DeepEvalBaseLLM

_GROQ_BASE = "https://api.groq.com/openai/v1"


class GroqEvalJudge(DeepEvalBaseLLM):
    """DeepEval-compatible judge backed by Groq via the openai SDK."""

    def __init__(self, model: str, api_key: str) -> None:
        self._model_name = model
        self._sync = OpenAI(api_key=api_key, base_url=_GROQ_BASE)
        self._async = AsyncOpenAI(api_key=api_key, base_url=_GROQ_BASE)

    def load_model(self):
        return self._sync

    def generate(self, prompt: str, *args, **kwargs) -> str:
        kwargs.pop("schema", None)
        resp = self._sync.chat.completions.create(
            model=self._model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content or ""

    async def a_generate(self, prompt: str, *args, **kwargs) -> str:
        kwargs.pop("schema", None)
        resp = await self._async.chat.completions.create(
            model=self._model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content or ""

    def get_model_name(self) -> str:
        return self._model_name
