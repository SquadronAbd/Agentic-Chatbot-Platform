"""
Batch evaluation script using real questions from questions.json.

Usage:
    python evaluate.py --questions path/to/questions.json --sample 10
    python evaluate.py --questions path/to/questions.json --all
"""
import argparse
import json
import random
import uuid
import sys
from pathlib import Path

# Bootstrap settings (loads .env, sets GROQ judge env vars)
from app.evaluation.evaluator import RAGEvaluator
from app.graph.workflow import build_graph
from app.memory.session import session_manager
from app.utils.logger import logger


def run_rag(question: str) -> tuple[str, list[str]]:
    """Send question through the LangGraph pipeline, return (answer, context_chunks)."""
    session_id = str(uuid.uuid4())
    graph = build_graph()
    state = graph.invoke(
        {
            "session_id": session_id,
            "question": question,
            "messages": [],
            "documents": [],
            "answer": "",
            "summary": "",
            "intent": "",
            "plan": [],
            "tool_results": [],
            "reflection_needed": False,
            "error": None,
        }
    )
    answer = state.get("answer", "")
    docs = state.get("documents", [])
    context = [d.page_content for d in docs if hasattr(d, "page_content")]
    return answer, context


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True, help="Path to questions.json")
    parser.add_argument("--sample", type=int, default=10, help="Number of random questions to evaluate")
    parser.add_argument("--all", action="store_true", help="Evaluate all questions")
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--output", default="eval_results.json", help="Where to save results")
    args = parser.parse_args()

    questions_path = Path(args.questions)
    if not questions_path.exists():
        print(f"File not found: {questions_path}")
        sys.exit(1)

    with open(questions_path, encoding="utf-8") as f:
        questions = json.load(f)

    selected = questions if args.all else random.sample(questions, min(args.sample, len(questions)))
    print(f"\nEvaluating {len(selected)} questions  (threshold={args.threshold})\n{'='*60}")

    evaluator = RAGEvaluator(threshold=args.threshold)
    results = []
    passed_counts = {}
    total_scores = {}

    for i, q in enumerate(selected, 1):
        text = q["text"]
        kind = q.get("kind", "")
        print(f"\n[{i}/{len(selected)}] {text[:90]}...")

        try:
            answer, context = run_rag(text)
            if not answer:
                print("  ⚠ Empty answer from RAG — skipping")
                continue

            scores = evaluator.score(
                query=text,
                actual_output=answer,
                retrieval_context=context if context else ["No context retrieved."],
            )

            result = {"question": text, "kind": kind, "answer": answer, "scores": scores}
            results.append(result)

            for metric, data in scores.items():
                score = data.get("score")
                passed = data.get("passed")
                symbol = "✓" if passed else "✗" if passed is False else "?"
                print(f"  {symbol} {metric:<30} score={score}")
                if score is not None:
                    total_scores.setdefault(metric, []).append(score)
                if passed is not None:
                    passed_counts.setdefault(metric, {"pass": 0, "fail": 0})
                    passed_counts[metric]["pass" if passed else "fail"] += 1

        except Exception as exc:
            logger.warning(f"Question {i} failed: {exc}")
            results.append({"question": text, "kind": kind, "error": str(exc)})

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for metric, scores in total_scores.items():
        avg = sum(scores) / len(scores)
        p = passed_counts.get(metric, {})
        total = p.get("pass", 0) + p.get("fail", 0)
        pass_rate = p.get("pass", 0) / total * 100 if total else 0
        print(f"  {metric:<30} avg={avg:.3f}  pass_rate={pass_rate:.0f}%  ({p.get('pass',0)}/{total})")

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path.resolve()}\n")


if __name__ == "__main__":
    main()
