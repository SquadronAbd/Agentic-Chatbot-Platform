from __future__ import annotations

from typing import Optional

from deepeval import evaluate as deepeval_run
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase
from loguru import logger

from app.config.settings import settings
from app.evaluation.groq_judge import GroqJudge

JUDGE_MODEL = "llama-3.3-70b-versatile"


def _make_judge() -> GroqJudge:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set — cannot run evaluation.")
    return GroqJudge(model=JUDGE_MODEL, api_key=settings.GROQ_API_KEY)


class RAGEvaluator:
    """
    Evaluates RAG pipeline output using five DeepEval metrics:

    - ContextualRelevancy  — are retrieved chunks relevant to the query?
    - ContextualPrecision  — are relevant chunks ranked above irrelevant ones?
    - ContextualRecall     — do chunks cover what the expected answer needs?
    - AnswerRelevancy      — does the final answer address the question?
    - Faithfulness         — is every claim in the answer grounded in context?
    """

    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold

    def _build_metrics(self, include_ground_truth: bool) -> list:
        judge = _make_judge()
        # These three work without any ground-truth expected output.
        metrics = [
            ContextualRelevancyMetric(threshold=self.threshold, model=judge),
            AnswerRelevancyMetric(threshold=self.threshold, model=judge),
            FaithfulnessMetric(threshold=self.threshold, model=judge),
        ]
        # ContextualPrecision and ContextualRecall both require expected_output.
        if include_ground_truth:
            metrics.append(ContextualPrecisionMetric(threshold=self.threshold, model=judge))
            metrics.append(ContextualRecallMetric(threshold=self.threshold, model=judge))
        return metrics

    def score(
        self,
        query: str,
        actual_output: str,
        retrieval_context: list[str],
        expected_output: Optional[str] = None,
    ) -> dict[str, dict]:
        """
        Run all applicable metrics and return per-metric scores.

        Args:
            query:             The user's original question.
            actual_output:     The answer produced by the RAG pipeline.
            retrieval_context: page_content strings of the retrieved chunks.
            expected_output:   Ground-truth answer (enables ContextualRecall).

        Returns:
            {
              "ContextualRelevancyMetric": {"score": 0.9, "passed": True, "reason": "..."},
              ...
            }
        """
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_output,
            expected_output=expected_output or "",
            retrieval_context=retrieval_context,
        )

        metrics = self._build_metrics(include_ground_truth=bool(expected_output))
        results: dict[str, dict] = {}

        for metric in metrics:
            name = type(metric).__name__
            try:
                metric.measure(test_case)
                results[name] = {
                    "score": metric.score,
                    "passed": metric.is_successful(),
                    "reason": getattr(metric, "reason", ""),
                }
            except Exception as exc:
                logger.warning(f"{name} failed: {exc}")
                results[name] = {"score": None, "passed": None, "reason": str(exc)}

        return results

    def batch_evaluate(self, test_cases: list[LLMTestCase]) -> None:
        """
        Run deepeval's full evaluation suite against a list of LLMTestCase objects.
        Outputs a summary report to stdout and writes results to deepeval's local store.
        """
        metrics = self._build_metrics(include_ground_truth=True)
        deepeval_run(test_cases, metrics)
