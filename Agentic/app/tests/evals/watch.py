"""
Watch mode: re-run evaluation automatically when dataset or judge prompts change.

Usage:
    cd Agentic
    python -m app.tests.evals.watch --once       # run once and exit
    python -m app.tests.evals.watch --interval 30 # poll every 30 seconds

What counts as "new":
  - A new example in the dataset (run_eval.py caches by example hash).
  - A changed judge prompt or rubric (rubric hash bumps, all examples re-run).

No external dependencies (no watchdog). Pure mtime polling — runs anywhere.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).parent

WATCH_PATHS = [
    EVAL_DIR / "run_eval.py",
    EVAL_DIR / "judges",   # directory of judge prompt .md files
    EVAL_DIR / "rubric.md",
]


def fingerprint(paths: list[Path]) -> tuple:
    prints: list[tuple[str, float]] = []
    for p in paths:
        if not p.exists():
            continue
        if p.is_file():
            prints.append((str(p), p.stat().st_mtime))
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    prints.append((str(f), f.stat().st_mtime))
    return tuple(prints)


def run_eval() -> int:
    print(f"\n=== eval triggered at {time.strftime('%H:%M:%S')} ===")
    return subprocess.call(
        [sys.executable, "-m", "app.tests.evals.run_eval"],
        cwd=EVAL_DIR.parents[3],  # Agentic/
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="Run once and exit.")
    p.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Poll interval in seconds (default 30).",
    )
    args = p.parse_args()

    if args.once:
        sys.exit(run_eval())

    last: tuple | None = None
    print(
        f"Watching {len(WATCH_PATHS)} paths. "
        f"Polling every {args.interval}s. Ctrl-C to stop."
    )
    try:
        while True:
            fp = fingerprint(WATCH_PATHS)
            if fp != last:
                rc = run_eval()
                print(f"=== eval finished (exit {rc}) ===")
                last = fp
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
