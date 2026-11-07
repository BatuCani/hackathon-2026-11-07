"""Engineer B run: M3 and M4 on every session -> results/engineer-b/ (plans/engineer-b.md Step 5).

    uv run --python 3.12 python scripts/run_b.py --seed 0 [--controls]

Uses Engineer A's loader (`toolbox.loader.load_sessions`) when it exists; otherwise runs on
labelled synthetic sessions and says so in summary.csv (column `data`). Results are generated
only by this script, never edited by hand.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

import numpy as np

from toolbox import m3_pca, m4_ica
from toolbox.assemblies import AssemblyParams
from toolbox.contract import _nan_to_none
from toolbox.controls import run_controls, scenario

OUT = Path(__file__).resolve().parents[1] / "results" / "engineer-b"
METHODS = {"M3": m3_pca.run_with_traces, "M4": m4_ica.run_with_traces}


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def load(seed: int):
    try:
        from toolbox.loader import load_sessions  # Engineer A
    except ImportError:
        names = ("positive", "pre_existing", "no_sleep_coactivity")
        return [scenario(n, seed=seed, tau_s=1.0) for n in names], "synthetic (loader not merged)"
    return list(load_sessions()), "real"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-shuffles", type=int, default=500)
    ap.add_argument("--controls", action="store_true", help="also run matched control sessions (20 seeds)")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    params = AssemblyParams(n_shuffles=args.n_shuffles)
    sessions, data = load(args.seed)
    sha = git_sha()
    rows = []
    for rec in sessions:
        for mid, run in METHODS.items():
            res, traces = run(rec, seed=args.seed, params=params)
            stem = f"{rec.session_id}__{mid}"
            (OUT / f"{stem}.json").write_text(res.to_json() + "\n")
            if traces is not None:
                np.savez_compressed(OUT / f"{stem}__R.npz", **traces)
            rows.append({
                "session_id": rec.session_id, "method_id": mid, "eligible": res.eligible, "reason": res.reason,
                "score": res.score, "p_n1": res.p_n1, "p_blockswap": res.details.get("p_blockswap", float("nan")),
                "n_sig": res.details.get("n_sig", ""), "n_shuffles": res.n_shuffles, "seed": res.seed,
                "git_sha": sha, "data": data,
            })
            print(f"{stem}: eligible={res.eligible} score={res.score:.4g} p_n1={res.p_n1:.4g} "
                  f"p_blockswap={rows[-1]['p_blockswap']:.4g} {res.reason}")

    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    if args.controls:
        reports = {mid: asdict(run_controls(mid, sessions[0], seed=args.seed, n_seeds=20, params=params))
                   for mid in METHODS}
        (OUT / "controls.json").write_text(json.dumps(_nan_to_none(reports), sort_keys=True, indent=1) + "\n")
        for mid, r in reports.items():
            print(f"controls {mid}: tpr={r['tpr']:.2f} fpr={r['fpr']} passed={r['passed']}")


if __name__ == "__main__":
    main()
