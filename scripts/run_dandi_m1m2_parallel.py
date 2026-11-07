"""M1 and M2 on the 8 DANDI:000044 sessions (positive control on real data) -> results/real/dandi/.

    OMP_NUM_THREADS=2 uv run --python 3.12 --with remfile python scripts/run_dandi_m1m2.py --seed 0

Writes <session>__M1.json, <session>__M2.json, M2_verdict.json, and appends M1/M2 rows to summary.csv
(M3/M4 rows from scripts/run_dandi.py are kept unchanged). Method defaults (500 shuffles).
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from toolbox import m1_pair_corr, m2_ev_rev
from toolbox.contract import MethodResult, _nan_to_none
from toolbox.loader_dandi import dandi_urls, load_dandi44

OUT = Path(__file__).resolve().parents[1] / "results" / "real" / "dandi"


def one_session(args) -> list[str]:
    url, seed = args
    rec = load_dandi44(url)
    out = []
    for mod in (m1_pair_corr, m2_ev_rev):
        res = mod.run(rec, seed=seed)
        path = OUT / f"{rec.session_id}__{res.method_id}.json"
        path.write_text(res.to_json() + "\n")
        out.append(res.to_json())
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    jobs = [(url, args.seed) for _, url in sorted(dandi_urls().items())]
    with ProcessPoolExecutor(args.workers) as ex:
        results = [MethodResult(**json.loads(j)) for js in ex.map(one_session, jobs) for j in js]

    m2 = [r for r in results if r.method_id == "M2"]
    v = m2_ev_rev.verdict(m2)
    ev = [r.details["ev"] for r in m2 if r.eligible]
    rev = [r.details["rev"] for r in m2 if r.eligible]
    v["ev_mean"], v["rev_mean"] = float(np.mean(ev)), float(np.mean(rev))
    v["ev_gt_rev_sessions"] = int(sum(e > r for e, r in zip(ev, rev)))
    (OUT / "M2_verdict.json").write_text(json.dumps(_nan_to_none(v), sort_keys=True, indent=1) + "\n")

    summary = OUT / "summary.csv"
    with open(summary, newline="") as f:
        old = [r for r in csv.DictReader(f) if r["method_id"] not in ("M1", "M2")]
    fields = list(old[0])
    for r in results:
        d = r.details or {}
        old.append({k: "" for k in fields} | {
            "session_id": r.session_id, "method_id": r.method_id, "n_cells": d.get("n_cells", ""),
            "eligible": r.eligible, "reason": r.reason, "score": r.score, "p_n1": r.p_n1,
            "p_blockswap": d.get("p_blockswap", ""), "n_shuffles": r.n_shuffles, "seed": r.seed, "git_sha": sha,
        })
    old.sort(key=lambda r: (r["session_id"], r["method_id"]))
    with open(summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(old)
    for r in sorted(results, key=lambda r: (r.session_id, r.method_id)):
        print(f"{r.session_id} {r.method_id}: eligible={r.eligible} score={r.score} p_n1={r.p_n1} "
              f"p_bs={(r.details or {}).get('p_blockswap')} {r.reason}")
    print("M2 verdict:", v["answer"], "| with blockswap:", v["answer_with_blockswap"],
          f"| mean EV {v['ev_mean']:.4f} vs REV {v['rev_mean']:.4f}, EV > REV in {v['ev_gt_rev_sessions']}/{len(ev)}")


if __name__ == "__main__":
    main()
