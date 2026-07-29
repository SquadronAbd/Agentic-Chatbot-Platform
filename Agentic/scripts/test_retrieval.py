"""
test_retrieval.py

Runs retrieval for every question in questions.json and prints results.
Logs are written automatically to logs/retrieval_YYYY-MM-DD.log via retrieval_logger.

Usage (from project root, venv active):
    python Agentic/scripts/test_retrieval.py
    python Agentic/scripts/test_retrieval.py --limit 5
    python Agentic/scripts/test_retrieval.py --kind boolean
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Make app importable and point pydantic-settings at the right .env
AGENTIC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTIC_DIR))

import os
os.environ.setdefault("ENV_FILE", str(AGENTIC_DIR / ".env"))

# Load .env manually before settings is imported
from dotenv import load_dotenv
load_dotenv(AGENTIC_DIR / ".env")

from app.rag.retriever import retriever

QUESTIONS_FILE = (
    Path(__file__).resolve().parents[2]
    / "backend" / "data" / "questions" / "questions.json"
)


def load_questions(kind: str | None = None, limit: int | None = None) -> list[dict]:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)
    if kind:
        questions = [q for q in questions if q.get("kind") == kind]
    if limit:
        questions = questions[:limit]
    return questions


def run(kind: str | None, limit: int | None) -> None:
    questions = load_questions(kind=kind, limit=limit)
    total = len(questions)
    print(f"Running retrieval for {total} question(s)...\n")

    for i, q in enumerate(questions, start=1):
        query = q["text"]
        print(f"[{i}/{total}] {query[:100]}...")

        t0 = time.perf_counter()
        docs = retriever.retrieve(query)
        elapsed = time.perf_counter() - t0

        print(f"  -> {len(docs)} chunks retrieved in {elapsed:.2f}s")
        if docs:
            preview = docs[0].page_content[:150].replace("\n", " ")
            print(f"  Top chunk: {preview}")
        print()

    print("Done. Check logs/retrieval_<date>.log for detailed per-query logs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test retrieval against questions.json")
    parser.add_argument("--limit", type=int, default=None, help="Max questions to run")
    parser.add_argument("--kind", type=str, default=None, help="Filter by question kind (number, boolean, names)")
    args = parser.parse_args()
    run(kind=args.kind, limit=args.limit)
