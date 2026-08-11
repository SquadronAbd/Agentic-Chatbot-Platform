"""
Shared fixtures for the conversational eval suite.

Run from the project root:
    deepeval test run Agentic/app/tests/evals/test_multiturn_eval.py

Or with plain pytest (skips Confident AI upload):
    pytest Agentic/app/tests/evals/ -v -m eval
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest
import deepeval

# ---------------------------------------------------------------------------
# Path & env setup — must happen before any app import
# ---------------------------------------------------------------------------
_agentic_root = Path(__file__).parent.parent.parent.parent  # Agentic/
if str(_agentic_root) not in sys.path:
    sys.path.insert(0, str(_agentic_root))

from dotenv import load_dotenv
load_dotenv(_agentic_root / ".env")

# Login to Confident AI once at import time (no-op if key absent)
_confident_key = os.getenv("DEEPEVAL_API_KEY", "")
if _confident_key:
    deepeval.login(api_key=_confident_key)

# ---------------------------------------------------------------------------
# App imports (after path/env are set)
# ---------------------------------------------------------------------------
from app.config.settings import settings  # noqa: E402
from .judge import GroqEvalJudge  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
async def async_client():
    """
    In-process ASGI client backed by the real FastAPI app.
    Module-scoped: the lifespan (DB + BM25 bootstrap) runs once per module.
    """
    import httpx
    from httpx import ASGITransport
    from app.main import app

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=120.0,
    ) as client:
        yield client


@pytest.fixture(scope="session")
def judge() -> GroqEvalJudge:
    if not settings.GROQ_API_KEY:
        pytest.skip("GROQ_API_KEY not set — skipping eval")
    return GroqEvalJudge(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
    )


@pytest.fixture
def fresh_session() -> str:
    """Unique session ID per test — prevents memory contamination between goldens."""
    return f"eval-{uuid.uuid4().hex[:10]}"
