from __future__ import annotations
import os
from typing import Optional

from app.config.settings import settings

# Use Groq as the LLM judge (OpenAI-compatible API).
# deepeval reads OPENAI_API_KEY + OPENAI_API_BASE to route requests.
if settings.GROQ_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", settings.GROQ_API_KEY)
    os.environ.setdefault("OPENAI_API_BASE", "https://api.groq.com/openai/v1")
elif settings.OPENAI_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", settings.OPENAI_API_KEY)

from deepeval import evaluate as deepeval_run
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.test_case import LLMTestCase
from loguru import logger


# deepeval uses an LLM judge to score each metric.
# By default it calls OpenAI.  To use a different model, set the
# OPENAI_API_KEY env var or configure a custom model via deepeval's
# `deepeval.login_with_confident_ai()` / `deepeval.set_local_model()`.


class RAGEvaluator:
    """
    Evaluates RAG pipeline output using four deepeval metrics:

    - AnswerRelevancy     — does the answer address the question?
    - Faithfulness        — is every claim grounded in retrieved context?
    - ContextualPrecision — are the retrieved chunks actually useful for the answer?
    - ContextualRecall    — do the chunks cover what the expected answer needs?
                           (requires expected_output; skipped when not provided)
    """

    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold

    JUDGE_MODEL = "llama-3.3-70b-versatile"

    def _build_metrics(self, include_recall: bool) -> list:
        metrics = [
            AnswerRelevancyMetric(threshold=self.threshold, model=self.JUDGE_MODEL),
            FaithfulnessMetric(threshold=self.threshold, model=self.JUDGE_MODEL),
            ContextualPrecisionMetric(threshold=self.threshold, model=self.JUDGE_MODEL),
        ]
        if include_recall:
            metrics.append(ContextualRecallMetric(threshold=self.threshold, model=self.JUDGE_MODEL))
        return metrics

    def score(
        self,
        query: str,
        actual_output: str,
        retrieval_context: list[str],
        expected_output: Optional[str] = None,
    ) -> dict[str, dict]:
        """
        Runs all applicable metrics and returns per-metric scores.

        Args:
            query:             The user's original question.
            actual_output:     The answer produced by the RAG pipeline.
            retrieval_context: The page_content strings of retrieved chunks.
            expected_output:   Ground-truth answer (enables ContextualRecall).

        Returns:
            {
              "AnswerRelevancyMetric": {"score": 0.9, "passed": True, "reason": "..."},
              ...
            }
        """
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=expected_output or "",
            retrieval_context=retrieval_context,
        )

        metrics = self._build_metrics(include_recall=bool(expected_output))
        results: dict[str, dict] = {}

        for metric in metrics:
            try:
                metric.measure(test_case)
                results[type(metric).__name__] = {
                    "score": metric.score,
                    "passed": metric.is_successful(),
                    "reason": getattr(metric, "reason", ""),
                }
            except Exception as exc:
                logger.warning(f"{type(metric).__name__} failed: {exc}")
                results[type(metric).__name__] = {"score": None, "passed": None, "reason": str(exc)}

        return results

    def batch_evaluate(self, test_cases: list[LLMTestCase]) -> None:
        """
        Runs deepeval's full evaluation suite against a list of LLMTestCase objects.
        Outputs a summary report to stdout and writes results to deepeval's local store.
        """
        metrics = self._build_metrics(include_recall=True)
        deepeval_run(test_cases, metrics)
