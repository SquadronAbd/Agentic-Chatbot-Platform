"""
Multi-turn conversational eval suite using DeepEval 4.x.

Run with:
    deepeval test run Agentic/app/tests/evals/test_multiturn_eval.py

Or plain pytest (no Confident AI upload):
    pytest Agentic/app/tests/evals/ -v -m eval

Each parametrised test:
  1. Simulates a full multi-turn conversation by calling the live /chat endpoint.
  2. Builds a ConversationalTestCase from interleaved user/assistant Turns.
  3. Measures applicable conversational metrics in parallel (async_mode=True).
  4. Invokes ReflectionAgent.reflect_on_eval_failure() for every metric that fails.
  5. Asserts all metrics pass — surfacing the reflection diagnosis in the failure message.
"""
from __future__ import annotations

import asyncio
from typing import List

import httpx
import pytest

from deepeval.test_case import ConversationalTestCase, Turn
from deepeval.metrics import (
    KnowledgeRetentionMetric,
    RoleAdherenceMetric,
    TurnRelevancyMetric,
    ConversationCompletenessMetric,
    TaskCompletionMetric,
    TurnFaithfulnessMetric,
)

from app.agents.reflection_agent import ReflectionAgent
from .goldens import GOLDENS, ConversationalGolden
from .judge import GroqEvalJudge

pytestmark = [pytest.mark.asyncio, pytest.mark.eval]

THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Conversation simulation
# ---------------------------------------------------------------------------

async def simulate_conversation(
    client: httpx.AsyncClient,
    session_id: str,
    golden: ConversationalGolden,
) -> ConversationalTestCase:
    """
    Drive the chatbot through every user turn in a golden and collect
    assistant responses, returning a fully populated ConversationalTestCase.
    """
    turns: List[Turn] = []

    for user_msg in golden.user_turns:
        turns.append(Turn(role="user", content=user_msg))

        resp = await client.post(
            "/chat",
            json={"session_id": session_id, "question": user_msg},
        )
        resp.raise_for_status()
        data = resp.json()

        answer: str = data.get("answer", "")
        retrieval_context: list[str] | None = [
            s["content"] for s in data.get("sources", []) if s.get("content")
        ] or None

        turns.append(
            Turn(
                role="assistant",
                content=answer,
                retrieval_context=retrieval_context,
            )
        )

    return ConversationalTestCase(
        turns=turns,
        scenario=golden.scenario,
        user_description=golden.user_description,
        chatbot_role=golden.chatbot_role,
        expected_outcome=golden.expected_outcome,
        name=golden.name,
        tags=golden.tags,
    )


# ---------------------------------------------------------------------------
# Metric selection
# ---------------------------------------------------------------------------

def build_metrics(judge: GroqEvalJudge, golden: ConversationalGolden) -> list:
    """Return the metric set appropriate for this golden's tags."""
    metrics = [
        TurnRelevancyMetric(threshold=THRESHOLD, model=judge),
        KnowledgeRetentionMetric(threshold=THRESHOLD, model=judge),
    ]
    if "faithfulness" in golden.tags or "hallucination-guard" in golden.tags:
        metrics.append(TurnFaithfulnessMetric(threshold=THRESHOLD, model=judge))
    if "role-adherence" in golden.tags or "off-topic" in golden.tags:
        metrics.append(RoleAdherenceMetric(threshold=THRESHOLD, model=judge))
    if "task-completion" in golden.tags:
        metrics.append(
            TaskCompletionMetric(
                threshold=THRESHOLD,
                model=judge,
                task=golden.expected_outcome,
            )
        )
    if "context-retention" in golden.tags or "multi-turn" in golden.tags:
        metrics.append(ConversationCompletenessMetric(threshold=THRESHOLD, model=judge))
    return metrics


# ---------------------------------------------------------------------------
# Parametrised test — one test per golden
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("golden", GOLDENS, ids=[g.name for g in GOLDENS])
async def test_multiturn_conversation(
    golden: ConversationalGolden,
    async_client: httpx.AsyncClient,
    judge: GroqEvalJudge,
    fresh_session: str,
) -> None:
    """
    Simulate the full conversation, measure all applicable metrics in parallel,
    and diagnose every failure via the ReflectionAgent before asserting.
    """
    test_case = await simulate_conversation(async_client, fresh_session, golden)
    metrics = build_metrics(judge, golden)

    # Measure all metrics concurrently (async_mode=True on each metric means
    # they fan out their own internal LLM calls; here we also fan out the
    # top-level measure calls for additional speed).
    await asyncio.gather(*(m.a_measure(test_case) for m in metrics))

    failed: list[str] = []
    reflector = ReflectionAgent()

    for metric in metrics:
        if metric.is_successful():
            continue

        reason: str = getattr(metric, "reason", "") or "no reason returned"
        last_user = next(
            (t.content for t in reversed(test_case.turns) if t.role == "user"), ""
        )
        last_bot = next(
            (t.content for t in reversed(test_case.turns) if t.role == "assistant"), ""
        )
        last_context = next(
            (
                t.retrieval_context
                for t in reversed(test_case.turns)
                if t.role == "assistant" and t.retrieval_context
            ),
            None,
        )

        diagnosis = await reflector.reflect_on_eval_failure(
            metric_name=type(metric).__name__,
            score=metric.score or 0.0,
            reason=reason,
            question=last_user,
            answer=last_bot,
            retrieval_context=last_context,
        )

        failed.append(
            f"\n{'─' * 60}"
            f"\nMETRIC  : {type(metric).__name__}"
            f"\nSCORE   : {metric.score:.3f}  (threshold={THRESHOLD})"
            f"\nREASON  : {reason}"
            f"\nDIAGNOSIS:\n{diagnosis}"
        )

    assert not failed, (
        f"[{golden.name}] {len(failed)} metric(s) failed:" + "".join(failed)
    )
