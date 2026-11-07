"""One-command reproduction of every result (task T8 in TASKS.md).

Usage, from a fresh clone:

    uv run python run.py --data /path/to/sleep_data.mat --seed 0

Loads Split A and Split B (PROBLEM.md), runs the method tests, runs M1-M4 with
N1 (500 shuffles), applies the verdict rule, and writes result JSON and the
results table to ``results/``. Not implemented yet: this stub fixes the interface.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, required=True, help="path to RIKEN sleep_data.mat")
    parser.add_argument("--seed", type=int, default=0, help="master seed (default 0)")
    parser.add_argument("--out", type=Path, default=Path("results"), help="output directory")
    args = parser.parse_args(argv)
    print(
        f"run.py: pipeline not implemented yet (data={args.data}, seed={args.seed}, out={args.out}); see TASKS.md T8",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
