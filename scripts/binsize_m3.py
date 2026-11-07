"""Loop 4: M3 on 3 DANDI:000044 sessions at 50/100/200 ms bins -> results/real/dandi_binsize.json + figure.

    OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/binsize_m3.py

200 shuffles (deviation from 500, see JOURNAL.md PREDICT Loop 4), seed 0, one process.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from toolbox import m3_pca
from toolbox.assemblies import AssemblyParams
from toolbox.loader_dandi import dandi_urls, load_dandi44

ROOT = Path(__file__).resolve().parents[1]
SESSIONS = ["Achilles_10252013", "Achilles_11012013", "Cicero_09102014"]
BINS = [0.05, 0.1, 0.2]
OUT = ROOT / "results" / "real" / "dandi_binsize.json"


def main() -> None:
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, cwd=ROOT).strip()
    urls = dandi_urls()
    rows = []
    for sid in SESSIONS:
        url = next(u for k, u in urls.items() if all(p in k for p in sid.split("_")))
        for b in BINS:
            rec = load_dandi44(url, bin_s=b)
            res = m3_pca.run(rec, seed=0, params=AssemblyParams(n_shuffles=200))
            yes = bool(res.eligible and res.score is not None and res.score > 0 and res.p_n1 < 0.05)
            row = {"session_id": rec.session_id, "bin_ms": int(round(b * 1000)), "n_cells": int(rec.deconv.shape[0]),
                   "eligible": res.eligible, "reason": res.reason, "D3": res.score, "p_n1": res.p_n1,
                   "n_sig": res.details.get("n_sig"), "yes": yes}
            rows.append(row)
            print(row, flush=True)
            OUT.write_text(json.dumps({"n_shuffles": 200, "seed": 0, "git_sha": sha, "rows": rows}, indent=2) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for sid in SESSIONS:
        r = [x for x in rows if x["session_id"] == sid]
        ax.plot([x["bin_ms"] for x in r], [x["D3"] for x in r], "o-", label=sid)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xscale("log"); ax.set_xticks([50, 100, 200]); ax.set_xticklabels(["50", "100", "200"])
    ax.set_xlabel("bin size (ms)"); ax.set_ylabel("M3 score D3"); ax.set_title("M3 vs bin size, DANDI:000044")
    ax.legend(fontsize=7); fig.tight_layout()
    fig.savefig(ROOT / "results" / "figures" / "binsize_m3.png", dpi=150)


if __name__ == "__main__":
    main()
