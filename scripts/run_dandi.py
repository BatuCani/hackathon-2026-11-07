"""M3 and M4 on the 8 DANDI:000044 sessions: positive control on real data -> results/real/dandi/.

    OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi.py --seed 0

Loader defaults (toolbox/loader_dandi.py): 100 ms bins, pyramidal cells, all MAZE bins as TASK.
AssemblyParams defaults (500 shuffles). One process per session.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from toolbox import m3_pca, m4_ica
from toolbox.assemblies import AssemblyParams
from toolbox.loader_dandi import dandi_urls, load_dandi44

OUT = Path(__file__).resolve().parents[1] / "results" / "real" / "dandi"
METHODS = {"M3": m3_pca.run_with_traces, "M4": m4_ica.run_with_traces}


def one_session(args) -> list[dict]:
    url, seed, sha = args
    rec = load_dandi44(url)
    rows = []
    for mid, run in METHODS.items():
        res, traces = run(rec, seed=seed, params=AssemblyParams())
        stem = f"{rec.session_id}__{mid}"
        (OUT / f"{stem}.json").write_text(res.to_json() + "\n")
        if traces is not None:
            np.savez_compressed(OUT / f"{stem}__R.npz", **traces)
        d = res.details
        rows.append({
            "session_id": rec.session_id, "method_id": mid, "n_cells": rec.deconv.shape[0],
            "eligible": res.eligible, "reason": res.reason, "score": res.score, "p_n1": res.p_n1,
            "p_blockswap": d.get("p_blockswap", float("nan")), "p_n1_pre_alone": d.get("p_n1_pre_alone", float("nan")),
            "p_n1_post_alone": d.get("p_n1_post_alone", float("nan")), "n_sig": d.get("n_sig", ""),
            "bound": d.get("bound", float("nan")), "n_shuffles": res.n_shuffles, "seed": seed, "git_sha": sha,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    jobs = [(url, args.seed, sha) for _, url in sorted(dandi_urls().items())]
    with ProcessPoolExecutor(args.workers) as ex:
        rows = [r for rs in ex.map(one_session, jobs) for r in rs]
    rows.sort(key=lambda r: (r["session_id"], r["method_id"]))
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"{r['session_id']} {r['method_id']}: eligible={r['eligible']} n_sig={r['n_sig']} "
              f"D={r['score']:.4g} p_n1={r['p_n1']:.4g} p_bs={r['p_blockswap']:.4g} {r['reason']}")


if __name__ == "__main__":
    main()
