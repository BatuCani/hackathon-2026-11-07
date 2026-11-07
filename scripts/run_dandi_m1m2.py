"""M1 and M2 on the 8 DANDI:000044 sessions (Loop 2) -> results/real/dandi/.

    OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi_m1m2.py --seed 0

Same loader settings as scripts/run_dandi.py (M3/M4): toolbox/loader_dandi.py defaults, 100 ms bins,
pyramidal cells, all MAZE bins as TASK; PRE/POST are NREM-only via contract.analysis_mask.
Method defaults (500 shuffles). One process, sessions in sequence. Rows are appended to summary.csv.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

from toolbox import m1_pair_corr, m2_ev_rev
from toolbox.loader_dandi import dandi_urls, load_dandi44

OUT = Path(__file__).resolve().parents[1] / "results" / "real" / "dandi"
METHODS = {"M1": m1_pair_corr.run, "M2": m2_ev_rev.run}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    with open(OUT / "summary.csv", newline="") as f:
        fields = next(csv.reader(f))
    for _, url in sorted(dandi_urls().items()):
        rec = load_dandi44(url)
        for mid, run in METHODS.items():
            res = run(rec, seed=args.seed)
            (OUT / f"{rec.session_id}__{mid}.json").write_text(res.to_json() + "\n")
            d = res.details
            row = {
                "session_id": rec.session_id, "method_id": mid, "n_cells": rec.deconv.shape[0],
                "eligible": res.eligible, "reason": res.reason, "score": res.score, "p_n1": res.p_n1,
                "p_blockswap": d.get("p_blockswap", float("nan")), "p_n1_pre_alone": float("nan"),
                "p_n1_post_alone": float("nan"), "n_sig": "", "bound": float("nan"),
                "n_shuffles": res.n_shuffles, "seed": args.seed, "git_sha": sha,
            }
            with open(OUT / "summary.csv", "a", newline="") as f:
                csv.DictWriter(f, fieldnames=fields).writerow(row)
            extra = f" EV={d['ev']:.4g} REV={d['rev']:.4g}" if mid == "M2" and res.eligible else ""
            print(f"{rec.session_id} {mid}: eligible={res.eligible} D={res.score:.4g} p_n1={res.p_n1:.4g}"
                  f"{extra} {res.reason}", flush=True)


if __name__ == "__main__":
    main()
