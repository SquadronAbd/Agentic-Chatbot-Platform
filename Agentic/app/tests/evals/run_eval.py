"""
LLM-as-judge evaluation harness for the Financial RAG Agent.

Judge: Groq llama-3.3-70b-versatile (OpenAI-compatible endpoint)
Criteria: Faithfulness (0.45), Refusal Correctness (0.30), Task Completion (0.25)
Rubric: Agentic/app/tests/evals/rubric.md
Prompts: Agentic/app/tests/evals/judges/

Usage:
    cd Agentic
    python -m app.tests.evals.run_eval

Requires: GROQ_API_KEY in env or Agentic/.env
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Load .env from Agentic/.env if present (for GROQ_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parents[4] / ".env")
except ImportError:
    pass

try:
    from openai import OpenAI
except ImportError:
    sys.exit("Missing dependency: pip install openai")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JUDGE_MODEL = "llama-3.3-70b-versatile"
JUDGE_MAX_TOKENS = 1024
JUDGE_TEMPERATURE = 0.0  # deterministic judging

EVAL_DIR = Path(__file__).parent
OUTPUT_PATH = EVAL_DIR / "results.json"

REGRESSION_THRESHOLD = 0.70
WEIGHTS = {
    "faithfulness": 0.45,
    "refusal_correctness": 0.30,
    "task_completion": 0.25,
}

JUDGES: list[dict[str, str]] = [
    {"name": "faithfulness",        "prompt_path": str(EVAL_DIR / "judges" / "faithfulness.md")},
    {"name": "refusal_correctness", "prompt_path": str(EVAL_DIR / "judges" / "refusal_correctness.md")},
    {"name": "task_completion",     "prompt_path": str(EVAL_DIR / "judges" / "task_completion.md")},
]

# Set to str(EVAL_DIR / "judges" / "attribution.md") to enable step attribution.
ATTRIBUTION_PROMPT_PATH: str | None = None


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Step:
    role: str
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Example:
    id: str
    input: str
    reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunResult:
    output: str
    retrieved_context: str = ""
    trajectory: list[Step] = field(default_factory=list)
    step_count: int = 0
    token_count: int | None = None
    wall_clock_s: float | None = None


@dataclass
class JudgeVerdict:
    criterion: str
    rationale: str
    score: Any
    ambiguous: bool
    evidence: list[str]
    raw: str


# ---------------------------------------------------------------------------
# Dataset — financial RAG eval examples
# ---------------------------------------------------------------------------

_EXAMPLES: list[dict[str, Any]] = [
    # --- Faithfulness tests ---
    {
        "id": "faith-01",
        "input": "What are the key financial metrics discussed in the documents?",
        "reference": None,
        "tags": ["faithfulness", "task_completion"],
    },
    {
        "id": "faith-02",
        "input": "What was the revenue mentioned in the reports?",
        "reference": None,
        "tags": ["faithfulness", "refusal_correctness"],
    },
    # --- Refusal correctness tests (answers NOT in typical test documents) ---
    {
        "id": "refusal-01",
        "input": "What was the personal net worth of the CEO in 2019?",
        "reference": "I couldn't find the answer in the provided documents.",
        "tags": ["refusal_correctness", "faithfulness"],
    },
    {
        "id": "refusal-02",
        "input": "List all internal employee salary bands across engineering levels.",
        "reference": "I couldn't find the answer in the provided documents.",
        "tags": ["refusal_correctness", "faithfulness"],
    },
    # --- Task completion tests (compound/multi-part questions) ---
    {
        "id": "compound-01",
        "input": (
            "What documents do you have access to, "
            "and what are the main topics they cover?"
        ),
        "reference": None,
        "tags": ["task_completion", "faithfulness"],
    },
    {
        "id": "compound-02",
        "input": (
            "Summarize the financial performance shown in the documents "
            "and highlight any risks mentioned."
        ),
        "reference": None,
        "tags": ["task_completion", "faithfulness"],
    },
]


def load_dataset() -> list[Example]:
    return [
        Example(
            id=ex["id"],
            input=ex["input"],
            reference=ex.get("reference"),
            metadata={"tags": ex.get("tags", [])},
        )
        for ex in _EXAMPLES
    ]


# ---------------------------------------------------------------------------
# System-under-test adapter — calls RAGService.ask() directly
# ---------------------------------------------------------------------------

def run_system_under_test(example: Example) -> RunResult:
    return asyncio.run(_run_rag_async(example))


async def _run_rag_async(example: Example) -> RunResult:
    try:
        from app.rag.rag_service import RAGService
    except ImportError as exc:
        raise RuntimeError(
            "Cannot import RAGService — run from inside the Agentic/ directory "
            f"(e.g. `python -m app.tests.evals.run_eval`): {exc}"
        )

    service = RAGService()
    session_id = f"eval_{uuid.uuid4().hex}"

    result = await service.ask(session_id=session_id, question=example.input)

    answer = result.get("answer", "")
    sources = result.get("sources", [])

    # Build a single retrieved-context string from the returned source chunks.
    context_parts: list[str] = []
    for i, src in enumerate(sources, 1):
        content = src.get("content") or src.get("page_content", "")
        source_name = src.get("source", f"chunk-{i}")
        if content:
            context_parts.append(f"[{i}] {source_name}\n{content}")
    retrieved_context = (
        "\n\n---\n\n".join(context_parts) if context_parts else "(no chunks retrieved)"
    )

    # Represent the retrieval call as a trajectory step so attribution can reference it.
    trajectory = [
        Step(
            role="tool",
            content="hybrid_retrieval",
            tool_results=[
                {"source": s.get("source", ""), "content": s.get("content", "")}
                for s in sources
            ],
        )
    ]

    return RunResult(
        output=answer,
        retrieved_context=retrieved_context,
        trajectory=trajectory,
        step_count=1,
    )


# ---------------------------------------------------------------------------
# Judge invocation — Groq via OpenAI-compatible endpoint
# ---------------------------------------------------------------------------

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _fill_template(template: str, question: str, answer: str, retrieved_context: str) -> str:
    """Replace {{question}}, {{answer}}, {{retrieved_context}} placeholders."""
    return (
        template
        .replace("{{question}}", question)
        .replace("{{answer}}", answer)
        .replace("{{retrieved_context}}", retrieved_context)
    )


def _parse_judge_response(raw: str, criterion: str) -> JudgeVerdict:
    match = _JSON_BLOCK_RE.search(raw)
    if not match:
        return JudgeVerdict(criterion, "(judge returned no JSON)", None, True, [], raw)
    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        return JudgeVerdict(criterion, f"(invalid JSON: {exc})", None, True, [], raw)
    # Each judge prompt uses a different evidence field name; collect whichever is present.
    evidence: list[str] = list(
        obj.get("unsupported_claims")
        or obj.get("dropped_parts")
        or obj.get("evidence")
        or []
    )
    return JudgeVerdict(
        criterion=criterion,
        rationale=obj.get("rationale", ""),
        score=obj.get("score"),
        ambiguous=bool(obj.get("ambiguous", False)),
        evidence=evidence,
        raw=raw,
    )


def run_judge(
    client: OpenAI,
    prompt_template: str,
    example: Example,
    result: RunResult,
    criterion: str,
) -> JudgeVerdict:
    filled = _fill_template(
        prompt_template,
        question=example.input,
        answer=result.output,
        retrieved_context=result.retrieved_context,
    )
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        max_tokens=JUDGE_MAX_TOKENS,
        temperature=JUDGE_TEMPERATURE,
        messages=[
            {"role": "system", "content": filled},
            {
                "role": "user",
                "content": "Please evaluate the answer above and return your JSON verdict.",
            },
        ],
    )
    raw = resp.choices[0].message.content or ""
    return _parse_judge_response(raw, criterion)


# ---------------------------------------------------------------------------
# Weighted aggregate
# ---------------------------------------------------------------------------

def _normalise(score: Any, criterion: str) -> float | None:
    if score is None:
        return None
    s = float(score)
    if criterion == "refusal_correctness":  # binary 0/1
        return s
    return s / 2.0  # 3-point 0–2 → 0–1


def compute_aggregate(verdicts: list[JudgeVerdict]) -> dict[str, Any]:
    weighted_sum = 0.0
    total_weight = 0.0
    per_criterion: dict[str, Any] = {}
    sticky_fail = False

    for v in verdicts:
        w = WEIGHTS.get(v.criterion, 0.0)
        norm = _normalise(v.score, v.criterion)
        per_criterion[v.criterion] = {
            "score": v.score,
            "normalised": norm,
            "weight": w,
        }
        if norm is not None:
            weighted_sum += w * norm
            total_weight += w
        if v.criterion == "refusal_correctness" and norm is not None and norm < 0.5:
            sticky_fail = True

    aggregate = weighted_sum / total_weight if total_weight > 0 else None
    return {
        "aggregate": aggregate,
        "pass": (aggregate is not None and aggregate >= REGRESSION_THRESHOLD),
        "sticky_fail": sticky_fail,
        "per_criterion": per_criterion,
    }


# ---------------------------------------------------------------------------
# Caching helpers (rubric hash + example hash → skip already-judged pairs)
# ---------------------------------------------------------------------------

def compute_rubric_hash(judge_prompts: dict[str, str]) -> str:
    h = hashlib.sha256()
    h.update(JUDGE_MODEL.encode())
    for name in sorted(judge_prompts):
        h.update(b"||")
        h.update(name.encode())
        h.update(judge_prompts[name].encode("utf-8"))
    return h.hexdigest()[:16]


def compute_example_hash(example: Example) -> str:
    h = hashlib.sha256()
    h.update(example.id.encode())
    h.update(b"||")
    h.update(example.input.encode())
    if example.reference:
        h.update(b"||")
        h.update(example.reference.encode())
    return h.hexdigest()[:16]


def load_cache(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(records, list):
        return {}
    return {
        f"{r.get('example_hash', '')}:{r.get('rubric_hash', '')}": r
        for r in records
        if r.get("example_hash") and r.get("rubric_hash")
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        sys.exit(
            "GROQ_API_KEY is not set. "
            "Export it or add it to Agentic/.env before running."
        )

    # Load judge prompt templates
    judge_prompts: dict[str, str] = {}
    for j in JUDGES:
        p = Path(j["prompt_path"])
        if not p.exists():
            sys.exit(f"Judge prompt not found: {p}")
        judge_prompts[j["name"]] = p.read_text(encoding="utf-8")

    rubric_hash = compute_rubric_hash(judge_prompts)
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    dataset = load_dataset()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache = load_cache(OUTPUT_PATH)

    all_records: list[dict[str, Any]] = []
    n_reused = 0

    for i, example in enumerate(dataset, 1):
        ex_hash = compute_example_hash(example)
        cache_key = f"{ex_hash}:{rubric_hash}"

        if cache_key in cache:
            print(f"[{i}/{len(dataset)}] {example.id} — cached, skipping")
            all_records.append(cache[cache_key])
            n_reused += 1
            continue

        print(f"[{i}/{len(dataset)}] {example.id} — running SUT ...")
        t0 = time.time()
        try:
            result = run_system_under_test(example)
        except Exception as exc:
            print(f"  SUT error: {exc}")
            continue
        result.wall_clock_s = time.time() - t0

        verdicts: list[JudgeVerdict] = []
        for j in JUDGES:
            try:
                v = run_judge(client, judge_prompts[j["name"]], example, result, j["name"])
            except Exception as exc:
                v = JudgeVerdict(j["name"], f"(judge error: {exc})", None, True, [], "")
            verdicts.append(v)
            flag = " ⚠ ambiguous" if v.ambiguous else ""
            print(f"  {j['name']}: score={v.score}{flag}")

        agg = compute_aggregate(verdicts)
        status = "PASS" if agg["pass"] else "FAIL"
        sticky = " [STICKY-FAIL refusal_correctness]" if agg["sticky_fail"] else ""
        agg_score = f"{agg['aggregate']:.2f}" if agg["aggregate"] is not None else "n/a"
        print(f"  aggregate={agg_score} → {status}{sticky}")

        all_records.append({
            "id": example.id,
            "example_hash": ex_hash,
            "rubric_hash": rubric_hash,
            "input": example.input,
            "reference": example.reference,
            "result": {
                "output": result.output,
                "retrieved_context": result.retrieved_context,
                "trajectory": [asdict(s) for s in result.trajectory],
                "step_count": result.step_count,
                "wall_clock_s": result.wall_clock_s,
            },
            "verdicts": [asdict(v) for v in verdicts],
            "aggregate": agg,
        })

    OUTPUT_PATH.write_text(
        json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nWrote {len(all_records)} records → {OUTPUT_PATH}")
    print(f"  {n_reused} reused from cache, {len(all_records) - n_reused} freshly evaluated")

    # Summary table
    print(f"\n{'id':<28} {'aggregate':>10} {'faith':>7} {'refusal':>8} {'task':>6} {'':>6}")
    print("-" * 68)
    for rec in all_records:
        agg = rec["aggregate"]
        pc = agg["per_criterion"]
        faith = pc.get("faithfulness", {}).get("score", "-")
        refusal = pc.get("refusal_correctness", {}).get("score", "-")
        task = pc.get("task_completion", {}).get("score", "-")
        agg_disp = f"{agg['aggregate']:.2f}" if agg.get("aggregate") is not None else "n/a"
        status = "PASS" if agg.get("pass") else "FAIL"
        print(
            f"{rec['id']:<28} {agg_disp:>10} "
            f"{str(faith):>7} {str(refusal):>8} {str(task):>6} {status:>6}"
        )


if __name__ == "__main__":
    main()
