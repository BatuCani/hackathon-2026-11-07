"""Overview figure: DANDI:000044 positive control next to RIKEN mouse05.

Reads results/real/M{3,4}_split{A,B}.json and results/real/dandi/summary.csv,
writes results/figures/positive_control_vs_riken.png.

    uv run --python 3.12 --with matplotlib python scripts/plot_overview.py
"""

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REAL = ROOT / "results" / "real"
OUT = ROOT / "results" / "figures" / "positive_control_vs_riken.png"
ALPHA = 0.05


def main() -> None:
    with open(REAL / "dandi" / "summary.csv") as fh:
        rows = list(csv.DictReader(fh))
    sessions = sorted({r["session_id"] for r in rows})
    fig, axes = plt.subplots(
        1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [3.2, 1]}, sharey=True
    )
    colors = {"M3": "#3b6fb6", "M4": "#d9822b"}
    width = 0.38

    ax = axes[0]
    for j, method in enumerate(("M3", "M4")):
        for i, s in enumerate(sessions):
            r = next(x for x in rows if x["session_id"] == s and x["method_id"] == method)
            score, p = float(r["score"]), float(r["p_n1"])
            x = i + (j - 0.5) * width
            ax.bar(x, score, width, color=colors[method], label=method if i == 0 else None)
            if p < ALPHA:
                ax.text(x, score + 0.003, "*", ha="center", va="bottom", fontsize=12)
    ax.set_xticks(range(len(sessions)))
    ax.set_xticklabels([s.replace("_", "\n") for s in sessions], fontsize=8)
    ax.set_title("DANDI:000044 rat CA1 ephys = positive control only\n"
                 "8/8 sessions significant for M3 and M4 (* = p_N1 < 0.05, 500 shuffles)",
                 fontsize=10)
    ax.set_ylabel("score: POST - PRE reactivation strength (D3 / D4)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(frameon=False)

    ax = axes[1]
    for j, method in enumerate(("M3", "M4")):
        for i, split in enumerate(("A", "B")):
            d = json.loads((REAL / f"{method}_split{split}.json").read_text())
            x = i + (j - 0.5) * width
            if d["eligible"]:
                ax.bar(x, d["score"], width, color=colors[method])
                ax.text(x, min(d["score"], 0) - 0.006, f"p={d['p_n1']:.2g}",
                        ha="center", va="top", fontsize=7)
            else:
                ax.text(x, 0.004, "ineligible", rotation=90, ha="center", va="bottom",
                        fontsize=8, color="#666666")
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(-0.17, None)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Split A", "Split B"])
    ax.set_title("RIKEN mouse05 calcium\nA: not significant, B: ineligible", fontsize=10)
    ax.axhline(0, color="black", linewidth=0.8)

    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
