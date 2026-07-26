"""
Batch evaluation script using real questions from questions.json.
Calls the running Agentic FastAPI server at localhost:8000.

Usage:
    python evaluate.py --questions path/to/questions.json --sample 10
    python evaluate.py --questions path/to/questions.json --all
"""
import argparse
import json
import os
import random
import sys
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(".env")

groq_key = os.getenv("GROQ_API_KEY", "")

from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase
from langchain_groq import ChatGroq


class GroqJudge(DeepEvalBaseLLM):
    """Wraps Groq's ChatGroq as a deepeval-compatible LLM judge."""

    def __init__(self):
        self.model = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=groq_key,
            temperature=0,
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        response = self.model.invoke(prompt)
        return response.content

    async def a_generate(self, prompt: str) -> str:
        response = await self.model.ainvoke(prompt)
        return response.content

    def get_model_name(self) -> str:
        return "llama-3.3-70b-versatile"


def build_metrics(threshold: float, judge: GroqJudge):
    return [
        AnswerRelevancyMetric(threshold=threshold, model=judge),
        FaithfulnessMetric(threshold=threshold, model=judge),
    ]


def ask_rag(question: str, host: str, session_id: str) -> tuple[str, list[str]]:
    resp = requests.post(
        f"{host}/chat",
        json={"session_id": session_id, "question": question},
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    answer = data.get("answer", "")
    sources = data.get("sources", [])
    context = [s.get("content", "") for s in sources if s.get("content")]
    return answer, context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True)
    parser.add_argument("--sample", type=int, default=10)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--output", default="eval_results.json")
    args = parser.parse_args()

    questions_path = Path(args.questions)
    if not questions_path.exists():
        print(f"File not found: {questions_path}")
        sys.exit(1)

    with open(questions_path, encoding="utf-8") as f:
        questions = json.load(f)

    selected = questions if args.all else random.sample(questions, min(args.sample, len(questions)))
    print(f"\nEvaluating {len(selected)} questions  (host={args.host}  threshold={args.threshold})")
    print("=" * 60)

    judge = GroqJudge()
    metrics = build_metrics(args.threshold, judge)
    results = []
    total_scores: dict[str, list[float]] = {}
    passed_counts: dict[str, dict] = {}
    session_id = str(uuid.uuid4())

    for i, q in enumerate(selected, 1):
        text = q["text"]
        kind = q.get("kind", "")
        print(f"\n[{i}/{len(selected)}] {text[:90]}...")

        try:
            answer, context = ask_rag(text, args.host, session_id)
            if not answer:
                print("  ⚠ Empty answer — skipping")
                continue

            test_case = LLMTestCase(
                input=text,
                actual_output=answer,
                retrieval_context=context if context else ["No context retrieved."],
            )

            print(f"  → Answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            scores: dict[str, dict] = {}
            for metric in metrics:
                name = type(metric).__name__
                try:
                    metric.measure(test_case)
                    scores[name] = {
                        "score": metric.score,
                        "passed": metric.is_successful(),
                        "reason": getattr(metric, "reason", ""),
                    }
                    symbol = "✓" if metric.is_successful() else "✗"
                    print(f"  {symbol} {name:<30} score={metric.score:.3f}")
                    total_scores.setdefault(name, []).append(metric.score)
                    passed_counts.setdefault(name, {"pass": 0, "fail": 0})
                    passed_counts[name]["pass" if metric.is_successful() else "fail"] += 1
                except Exception as exc:
                    print(f"  ? {name:<30} error: {exc}")
                    scores[name] = {"score": None, "passed": None, "reason": str(exc)}

            results.append({"question": text, "kind": kind, "answer": answer, "scores": scores})

        except Exception as exc:
            print(f"  ✗ RAG call failed: {exc}")
            results.append({"question": text, "kind": kind, "error": str(exc)})

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for metric_name, scores in total_scores.items():
        avg = sum(scores) / len(scores)
        p = passed_counts.get(metric_name, {})
        total = p.get("pass", 0) + p.get("fail", 0)
        pass_rate = p.get("pass", 0) / total * 100 if total else 0
        print(f"  {metric_name:<30} avg={avg:.3f}  pass_rate={pass_rate:.0f}%  ({p.get('pass',0)}/{total})")

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path.resolve()}\n")


if __name__ == "__main__":
    main()
