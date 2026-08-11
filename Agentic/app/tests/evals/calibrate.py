"""
Calibration: compare LLM judge scores against human labels.

Usage:
    python -m app.tests.evals.calibrate \\
        --human app/tests/evals/human_labels.csv \\
        --judge app/tests/evals/results.json

Expected human CSV columns:
    id,criterion,score

Expected judge JSON: output of run_eval.py (list of records with `verdicts`).

Prints per-criterion agreement:
  - Cohen's kappa  for categorical scales (binary, 3-point)
  - Spearman rho   for numeric scales
  - Raw agreement  always shown for reference

Targets: kappa >= 0.6 for categorical, Spearman >= 0.7 for numeric.
If below target, iterate on the judge prompt or rubric anchors.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def cohens_kappa(a: list, b: list) -> float:
    assert len(a) == len(b) and a, "need equal non-empty sequences"
    labels = sorted(set(a) | set(b), key=str)
    idx = {label: i for i, label in enumerate(labels)}
    n = len(labels)
    mat = [[0] * n for _ in range(n)]
    for x, y in zip(a, b):
        mat[idx[x]][idx[y]] += 1
    total = len(a)
    observed = sum(mat[i][i] for i in range(n)) / total
    row = [sum(mat[i]) / total for i in range(n)]
    col = [sum(mat[i][j] for i in range(n)) / total for j in range(n)]
    expected = sum(row[i] * col[i] for i in range(n))
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


def spearman(a: list[float], b: list[float]) -> float:
    assert len(a) == len(b) and a

    def ranks(xs: list[float]) -> list[float]:
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    ra, rb = ranks(a), ranks(b)
    mean_a = sum(ra) / len(ra)
    mean_b = sum(rb) / len(rb)
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(ra, rb))
    den_a = math.sqrt(sum((x - mean_a) ** 2 for x in ra))
    den_b = math.sqrt(sum((y - mean_b) ** 2 for y in rb))
    if den_a == 0 or den_b == 0:
        return 0.0
    return num / (den_a * den_b)


def is_numeric(xs: list) -> bool:
    try:
        [float(x) for x in xs]
        return True
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Compare judge scores in results.json against human_labels.csv"
    )
    p.add_argument("--human", required=True, help="CSV with columns: id,criterion,score")
    p.add_argument(
        "--judge",
        default=str(Path(__file__).parent / "results.json"),
        help="results.json from run_eval.py (default: evals/results.json)",
    )
    args = p.parse_args()

    # Load human labels
    human: dict[tuple[str, str], str] = {}
    with open(args.human, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            human[(row["id"], row["criterion"])] = row["score"]

    # Load judge results
    records = json.loads(Path(args.judge).read_text(encoding="utf-8"))
    judge: dict[tuple[str, str], object] = {}
    for rec in records:
        for v in rec.get("verdicts", []):
            judge[(rec["id"], v["criterion"])] = v["score"]

    # Align by (id, criterion)
    by_crit: dict[str, list[tuple[object, object]]] = defaultdict(list)
    for (ex_id, crit), h_score in human.items():
        j_score = judge.get((ex_id, crit))
        if j_score is None:
            print(f"  warning: no judge score for ({ex_id}, {crit}), skipping")
            continue
        by_crit[crit].append((h_score, j_score))

    if not by_crit:
        print("No overlapping (id, criterion) pairs between human labels and judge results.")
        return

    KAPPA_TARGET = 0.6
    SPEARMAN_TARGET = 0.7

    print(f"\n{'criterion':<24} {'n':>4}  {'agreement':>10}  {'metric':<20}  {'target':>8}")
    print("-" * 72)
    for crit, pairs in sorted(by_crit.items()):
        h = [pr[0] for pr in pairs]
        j = [pr[1] for pr in pairs]
        agree = sum(1 for a, b in zip(h, j) if str(a) == str(b)) / len(pairs)
        if is_numeric(h) and is_numeric(j):
            metric_val = spearman([float(x) for x in h], [float(x) for x in j])
            label = f"spearman={metric_val:+.3f}"
            ok = metric_val >= SPEARMAN_TARGET
            target = f">= {SPEARMAN_TARGET}"
        else:
            metric_val = cohens_kappa(h, j)
            label = f"kappa={metric_val:+.3f}"
            ok = metric_val >= KAPPA_TARGET
            target = f">= {KAPPA_TARGET}"
        status = "OK" if ok else "BELOW TARGET"
        print(
            f"{crit:<24} {len(pairs):>4}  {agree:>9.1%}  {label:<20}  "
            f"{target:>8}  {status}"
        )

    print(
        "\nIf any criterion is BELOW TARGET, revise that judge prompt's anchor definitions "
        "and re-run calibration."
    )


if __name__ == "__main__":
    main()
