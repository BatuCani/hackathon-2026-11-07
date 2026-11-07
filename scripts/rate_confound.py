"""Loop 3: is the M3 'yes' on DANDI:000044 explained by a PRE -> POST NREM firing-rate change?

    OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile --with matplotlib python scripts/rate_confound.py

Rate ratio per session = mean POST NREM rate / mean PRE NREM rate over the analysed cells
(loader defaults, contract.analysis_mask). Pearson r(log rate ratio, D3) across the 8 sessions,
D3 from results/real/dandi/summary.csv. RIKEN Split A and B ratios are reported, not tested.
Writes results/real/rate_confound.json and results/figures/rate_confound.png.
--plot-only redraws the figure from the JSON without loading data.
"""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from toolbox.contract import analysis_mask
from toolbox.loader import load_sessions
from toolbox.loader_dandi import dandi_urls, load_dandi44

ROOT = Path(__file__).resolve().parents[1]


def rates(rec) -> dict:
    pre = rec.deconv[:, analysis_mask(rec, "PRE")].mean(axis=1) * rec.fs
    post = rec.deconv[:, analysis_mask(rec, "POST")].mean(axis=1) * rec.fs
    ok = (pre > 0) & (post > 0)
    return {
        "n_cells": int(rec.deconv.shape[0]),
        "mean_pre": float(pre.mean()),
        "mean_post": float(post.mean()),
        "rate_ratio": float(post.mean() / pre.mean()),
        "log_rate_ratio": float(np.log(post.mean() / pre.mean())),
        "median_cell_log_ratio": float(np.median(np.log(post[ok] / pre[ok]))),
    }


def verdict(r: float, p: float) -> str:
    if r > 0.7 and p < 0.05:
        return "rate confound supported"
    if abs(r) < 0.3 or p >= 0.05:
        return "not supported"
    return "not enough evidence"


def main() -> None:
    d3 = {}
    with open(ROOT / "results/real/dandi/summary.csv") as f:
        for row in csv.DictReader(f):
            if row["method_id"] == "M3":
                d3[row["session_id"]] = float(row["score"])
    dandi = {}
    for _, url in sorted(dandi_urls().items()):
        rec = load_dandi44(url)
        dandi[rec.session_id] = {**rates(rec), "D3": d3[rec.session_id], "unit": "Hz"}
        print(rec.session_id, dandi[rec.session_id])
    riken = {}
    for rec in load_sessions():
        riken[rec.session_id] = {**rates(rec), "unit": "deconvolved activity x fs (not a spike rate)"}
        print(rec.session_id, riken[rec.session_id])

    sids = sorted(dandi)
    x = np.array([dandi[s]["log_rate_ratio"] for s in sids])
    y = np.array([dandi[s]["D3"] for s in sids])
    r, p = stats.pearsonr(x, y)
    out = {
        "question": "Is the M3 D3 on 8 DANDI:000044 sessions explained by a PRE->POST NREM rate change?",
        "rule": "supported if r > 0.7 and p < 0.05; not supported if |r| < 0.3 or p >= 0.05; else not enough evidence",
        "n": len(sids), "pearson_r": float(r), "p": float(p), "verdict": verdict(r, p),
        "git_sha": subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, cwd=ROOT).strip(),
        "dandi": dandi, "riken": riken,
    }
    (ROOT / "results/real/rate_confound.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"r = {r:.3f}, p = {p:.3g}: {out['verdict']}")

    plot(out)


# Label offsets in points (dx, dy, ha), chosen so no label overlaps another or leaves the axes.
LABEL_POS = {
    "Achilles_10252013": (6, -3, "left"),
    "Achilles_11012013": (-6, -3, "right"),
    "Buddy_06272013": (0, -11, "center"),
    "Cicero_09012014": (0, 7, "center"),
    "Cicero_09102014": (6, -3, "left"),
    "Cicero_09172014": (0, -11, "center"),
    "Gatsby_08022013": (6, -3, "left"),
    "Gatsby_08282013": (6, -3, "left"),
}


def plot(out: dict) -> None:
    sids = sorted(out["dandi"])
    x = np.array([out["dandi"][s]["log_rate_ratio"] for s in sids])
    y = np.array([out["dandi"][s]["D3"] for s in sids])
    fig, ax = plt.subplots(figsize=(5, 3.6), dpi=150)
    ax.scatter(x, y, color="#2a6fb0", zorder=3)
    for s, xi, yi in zip(sids, x, y):
        dx, dy, ha = LABEL_POS.get(s, (5, 3, "left"))
        ax.annotate(s, (xi, yi), fontsize=6, xytext=(dx, dy), textcoords="offset points", ha=ha, va="center")
    ax.axvline(0, color="#999", lw=0.8, ls="--")
    ax.set_xlim(x.min() - 0.03, x.max() + 0.05)
    ax.set_ylim(y.min() - 0.012, y.max() + 0.01)
    ax.set_xlabel("log(POST NREM rate / PRE NREM rate)")
    ax.set_ylabel("M3 score D3")
    ax.set_title(f"DANDI:000044, n = {out['n']}: r = {out['pearson_r']:.2f}, p = {out['p']:.2g}", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/rate_confound.png")

if __name__ == "__main__":
    import sys

    if "--plot-only" in sys.argv:  # redraw the figure from results/real/rate_confound.json
        plot(json.loads((ROOT / "results/real/rate_confound.json").read_text()))
    else:
        main()
