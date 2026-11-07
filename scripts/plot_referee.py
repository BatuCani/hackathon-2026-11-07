#!/usr/bin/env python3
"""Referee figures for the demo, plus the real-data bar once results exist.

    uv run --python 3.12 --with matplotlib python scripts/plot_referee.py

Deterministic: NumPy seed 0, and every shuffle stream comes from toolbox.nulls.rng_for.
One core: BLAS threads are pinned before NumPy is imported.
Reads results/engineer-b and results/real when those files exist.
Recomputes only the synthetic panels those files do not already contain.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from toolbox.assemblies import (
    correlation,
    eigh_desc,
    mean_strength,
    n1_eigen_bound,
    reactivation_strength,
    significant_subspace,
    strength_test,
    zscore,
    AssemblyParams,
)
from toolbox.contract import analysis_mask
from toolbox.controls import scenario
from toolbox.m4_ica import ICANotConverged, ICAParams, ica_weights
from toolbox.nulls import circular_shift, n1_offsets, n1_pvalue, rng_for
from toolbox.synth import make_session

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "results" / "figures"
ENGINEER_B = REPO / "results" / "engineer-b"
REAL = REPO / "results" / "real"

SEED = 0
ALPHA = 0.05
N_SEEDS = 20
N_SHUFFLES = 100
EIGEN_SHUFFLES = 200
SMOOTH_S = 5.0
PASS_TPR = 0.9
PASS_FPR = 0.1

CASES = (
    ("positive", "Positive"),
    ("no_sleep_coactivity", "No sleep\nco-activity"),
    ("pre_existing", "Pre-existing"),
    ("other_assemblies", "Other\nassemblies"),
    ("noise_only", "Noise only"),
    ("reversed", "Reversal"),
)

METHOD_COLORS = {"M3": "#1F4E79", "M4": "#E07A3D"}
SPLIT_COLORS = ("#1F4E79", "#C44900", "#2E7D4F", "#6C3483")
EPOCH_COLORS = {"PRE": "#1F4E79", "TASK": "#B8860B", "POST": "#C44900"}


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=10)
    ax.xaxis.label.set_size(12)
    ax.yaxis.label.set_size(12)
    ax.title.set_size(13)


def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {path.relative_to(REPO)}")


def _null_scores(W, sub, params: AssemblyParams, seed: int, session_id: str) -> np.ndarray:
    """Same N1 score null as toolbox.assemblies.strength_test, kept for the histogram."""
    rng = rng_for(seed, session_id, "n1_strength")
    z_pre, z_post = sub.Z["PRE"], sub.Z["POST"]
    off_pre = n1_offsets(*z_pre.shape, params.n_shuffles, rng, params.min_shift)
    off_post = n1_offsets(*z_post.shape, params.n_shuffles, rng, params.min_shift)
    null_pre = np.array([mean_strength(W, circular_shift(z_pre, o)).mean() for o in off_pre])
    null_post = np.array([mean_strength(W, circular_shift(z_post, o)).mean() for o in off_post])
    return null_post - null_pre


def _is_yes(score: float, p_n1: float, p_blockswap: float) -> bool:
    return bool(score > 0 and p_n1 < ALPHA and p_blockswap < ALPHA)


def _smooth(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1 or x.size < win:
        return x
    kernel = np.ones(win) / win
    return np.convolve(x, kernel, mode="same")


def plot_eigenvalue_bounds(path: Path) -> dict:
    """T-N1-8 spectrum: calcium-like noise, no assemblies, seed 0."""
    rec = make_session(assemblies=(), tau_s=1.0, seed=SEED, session_id=f"synth-{SEED}")
    z_task = zscore(rec.deconv[:, analysis_mask(rec, "TASK")])
    bound = n1_eigen_bound(
        z_task,
        n_shuffles=EIGEN_SHUFFLES,
        quantile=0.95,
        rng=rng_for(SEED, rec.session_id, "eigen_bound"),
    )
    eig, _ = eigh_desc(correlation(z_task))
    n_mp = int(np.sum(eig > bound.mp_bound))
    n_n1 = int(np.sum(eig > bound.bound))
    rank = np.arange(1, eig.size + 1)

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    above = eig > bound.mp_bound
    ax.plot(rank, eig, color="#1F4E79", lw=1.6, marker="o", ms=3.5, label="TASK eigenvalue")
    ax.plot(
        rank[above],
        eig[above],
        color="#9B2226",
        lw=0,
        marker="o",
        ms=5.5,
        label=f"above Marchenko-Pastur ({n_mp})",
        zorder=3,
    )
    ax.axhline(
        bound.mp_bound,
        color="#9B2226",
        ls="--",
        lw=1.4,
        label=f"Marchenko-Pastur bound {bound.mp_bound:.2f}",
    )
    ax.axhline(bound.bound, color="#1B7F4E", ls="-", lw=1.6, label=f"N1 bound {bound.bound:.2f} ({n_n1} above)")
    ax.set_xlabel("component rank (1 = largest)")
    ax.set_ylabel("eigenvalue (correlation matrix, dimensionless)")
    if n_mp >= 5 and n_n1 == 0:
        title = "Marchenko-Pastur flags false components; the N1 bound does not"
    else:
        title = f"Eigenvalue spectrum: {n_mp} components above MP, {n_n1} above N1"
    ax.set_title(title)
    ax.set_xlim(0.5, eig.size + 0.5)
    ax.set_ylim(float(eig.min()) - 0.08, bound.bound + 0.28)
    _style(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    fig.text(
        0.01,
        -0.02,
        f"Synthetic TASK, no assemblies, tau_s = 1 s, N = {z_task.shape[0]} cells, "
        f"B = {z_task.shape[1]} frames, seed {SEED}, {EIGEN_SHUFFLES} N1 shuffles (T-N1-8).",
        fontsize=8,
        color="#333333",
    )
    _save(fig, path)
    return {"n_mp": n_mp, "n_n1": n_n1, "mp_bound": bound.mp_bound, "n1_bound": bound.bound}


def _m4_yes(sub, params: AssemblyParams, seed: int, session_id: str) -> bool:
    if sub.n_sig < 2:
        return False
    try:
        weights = ica_weights(sub, ICAParams(), rng_for(seed, session_id, "ica"))
    except ICANotConverged:
        return False
    tested = strength_test(weights, sub, params, seed=seed, session_id=session_id)
    return _is_yes(tested["score"], tested["p_n1"], tested["p_blockswap"])


def control_rates(params: AssemblyParams) -> tuple[dict, dict]:
    """Yes-fraction per case, plus the seed-0 positive M3 example (traces and null)."""
    rates = {key: {"M3": 0, "M4": 0} for key, _ in CASES}
    example = None
    for key, _label in CASES:
        t0 = time.perf_counter()
        for seed in range(N_SEEDS):
            rec = scenario(key, seed=seed, tau_s=1.0)
            sub = significant_subspace(rec, params, seed)
            if not hasattr(sub, "Z"):
                continue
            if sub.n_sig >= 1:
                weights = sub.V_sig
                tested = strength_test(weights, sub, params, seed=seed, session_id=rec.session_id)
                yes = _is_yes(tested["score"], tested["p_n1"], tested["p_blockswap"])
                rates[key]["M3"] += int(yes)
                if key == "positive" and seed == SEED:
                    null = _null_scores(weights, sub, params, seed, rec.session_id)
                    got = n1_pvalue(tested["score"], null)
                    if abs(got - tested["p_n1"]) > 1e-9:
                        raise RuntimeError(f"null p {got} != method p {tested['p_n1']}")
                    example = {
                        "score": float(tested["score"]),
                        "p_n1": float(tested["p_n1"]),
                        "p_blockswap": float(tested["p_blockswap"]),
                        "null": null,
                        "fs": float(sub.fs_bins),
                        "traces": {
                            ep: reactivation_strength(weights, sub.Z[ep]) for ep in ("PRE", "TASK", "POST")
                        },
                        "source": "recomputed positive control, seed 0",
                    }
            rates[key]["M4"] += int(_m4_yes(sub, params, seed, rec.session_id))
        print(f"  {key}: M3 {rates[key]['M3']}/{N_SEEDS}  M4 {rates[key]['M4']}/{N_SEEDS}  ({time.perf_counter() - t0:.1f}s)")
    for key in rates:
        rates[key] = {m: rates[key][m] / N_SEEDS for m in ("M3", "M4")}
    if example is None:
        raise RuntimeError("positive control seed 0 produced no M3 components")
    saved = _load_saved_traces()
    if saved is not None:
        example["traces"] = saved["traces"]
        example["fs"] = saved["fs"]
        example["source"] = saved["source"]
    return rates, example


def _load_saved_traces() -> dict | None:
    """Use an engineer-b npz when it already holds PRE, TASK and POST."""
    if not ENGINEER_B.is_dir():
        return None
    candidates = sorted(ENGINEER_B.glob("*positive*M3*R.npz")) or sorted(ENGINEER_B.glob("*M3*__R.npz"))
    for path in candidates:
        with np.load(path) as blob:
            keys = set(blob.files)
            if not {"R_pre", "R_task", "R_post"} <= keys:
                continue
            fs = float(blob["fs_bins"]) if "fs_bins" in keys else 10.0
            traces = {ep: np.array(blob[f"R_{ep.lower()}"]) for ep in ("PRE", "TASK", "POST")}
        return {"traces": traces, "fs": fs, "source": str(path.relative_to(REPO))}
    return None


def plot_controls(rates: dict, path: Path) -> None:
    labels = [label for _key, label in CASES]
    x = np.arange(len(CASES))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    for shift, method in ((-width / 2, "M3"), (width / 2, "M4")):
        heights = [rates[key][method] for key, _ in CASES]
        bars = ax.bar(x + shift, heights, width=width, color=METHOD_COLORS[method], label=method)
        for bar, height in zip(bars, heights):
            if height <= 0:
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#222222",
            )
    for i, (key, _label) in enumerate(CASES):
        if rates[key]["M3"] == 0 and rates[key]["M4"] == 0:
            ax.text(i, 0.025, "0", ha="center", va="bottom", fontsize=8, color="#222222")
    ax.axhline(PASS_TPR, color="#1B7F4E", ls="--", lw=1.2, label=f"pass, true-positive rate {PASS_TPR:.1f}")
    ax.axhline(PASS_FPR, color="#9B2226", ls=":", lw=1.4, label=f"pass, false-positive rate {PASS_FPR:.1f}")
    pos = min(rates["positive"]["M3"], rates["positive"]["M4"])
    neg = max(rates[key][method] for key, _ in CASES if key != "positive" for method in ("M3", "M4"))
    if pos >= PASS_TPR and neg <= PASS_FPR:
        title = "M3 and M4 pass: the positive control says yes, the negatives stay under 0.1"
    elif pos >= PASS_TPR:
        title = "Positive control clears 0.9; the negative controls stay near the 0.1 line"
    else:
        title = "Control cases: fraction of seeds that call reactivation"
    ax.set_title(title)
    ax.set_ylabel("fraction of seeds saying yes")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.18)
    ax.set_xlabel("control case (synthetic, tau_s = 1 s)")
    _style(ax)
    ax.legend(frameon=False, ncol=2, fontsize=9)
    fig.text(
        0.01,
        -0.04,
        f"Yes = eligible, score > 0, p_N1 < {ALPHA:.2f} and p_block-swap < {ALPHA:.2f}. "
        f"{N_SEEDS} seeds, {N_SHUFFLES} shuffles, master seed {SEED}. "
        "The green line is the pass for the positive case; the red line is the pass for every other case.",
        fontsize=8,
        color="#333333",
    )
    _save(fig, path)


def plot_reactivation(example: dict, path: Path) -> None:
    traces = example["traces"]
    fs = example["fs"]
    win = max(1, int(round(SMOOTH_S * fs)))
    means = {ep: float(traces[ep].mean()) for ep in ("PRE", "TASK", "POST")}
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 4.8), sharey=True)
    shown_mean = False
    mean_traces = []
    for ax, ep in zip(axes, ("PRE", "TASK", "POST")):
        series = traces[ep]
        t = np.arange(series.shape[1]) / fs
        for k in range(series.shape[0]):
            ax.plot(t, _smooth(series[k], win), color=EPOCH_COLORS[ep], lw=0.8, alpha=0.35, zorder=2)
        mean_trace = _smooth(series.mean(axis=0), win)
        mean_traces.append(mean_trace)
        ax.plot(t, mean_trace, color="#111111", lw=1.8, zorder=3, label="mean across components")
        ax.axhline(
            means[ep],
            color=EPOCH_COLORS[ep],
            ls="--",
            lw=1.8,
            zorder=4,
            label="unsmoothed epoch mean" if not shown_mean else None,
        )
        shown_mean = True
        ax.set_title(f"{ep}  mean {means[ep]:.3f} a.u.")
        ax.set_xlabel("time (s)")
        _style(ax)
    axes[0].set_ylabel("R(t) (squared z-score, a.u.)")
    stacked = np.concatenate(mean_traces)
    lo = min(float(np.percentile(stacked, 5)), min(means.values()))
    hi = max(float(np.percentile(stacked, 95)), max(means.values()))
    span = max(hi - lo, 0.05)
    axes[0].set_ylim(lo - 0.35 * span, hi + 0.45 * span)
    if means["POST"] > means["PRE"]:
        title = "Positive control: mean reactivation strength is higher in POST than in PRE"
    else:
        title = "Positive control: reactivation strength in PRE, TASK and POST"
    fig.suptitle(title, fontsize=13, y=1.04)
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.text(
        0.01,
        -0.08,
        f"Traces are a {SMOOTH_S:.0f} s moving average, and the y-axis is zoomed to that mean. "
        f"Dashed lines are the unsmoothed epoch means inside the M3 score "
        f"(POST - PRE = {means['POST'] - means['PRE']:.3f} a.u.). Source: {example['source']}.",
        fontsize=8,
        color="#333333",
    )
    _save(fig, path)


def plot_null(example: dict, path: Path) -> None:
    null = np.asarray(example["null"], dtype=float)
    score = float(example["score"])
    p_value = float(example["p_n1"])
    lo = min(float(null.min()), score)
    hi = max(float(null.max()), score)
    pad = 0.08 * (hi - lo + 1e-9)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.hist(null, bins=20, range=(lo - pad, hi + pad), color="#4C566A", edgecolor="white", label="N1 null scores")
    ax.axvline(score, color="#9B2226", lw=2.0, label=f"observed score {score:.3f}")
    ymax = ax.get_ylim()[1]
    ax.annotate(
        f"p = {p_value:.3f}",
        xy=(score, ymax * 0.92),
        xytext=(-8, 0),
        textcoords="offset points",
        color="#9B2226",
        fontsize=12,
        ha="right",
        va="top",
    )
    ax.set_xlabel("M3 score (mean R in POST minus mean R in PRE, a.u.)")
    ax.set_ylabel("number of shuffles")
    if score > 0 and p_value < ALPHA:
        title = "Observed M3 score sits in the upper tail of the N1 null"
    else:
        title = "N1 null distribution of the M3 score on the positive control"
    ax.set_title(title)
    _style(ax)
    ax.legend(frameon=False, fontsize=9)
    fig.text(
        0.01,
        -0.03,
        f"Positive control, seed {SEED}, {null.size} circular-shift shuffles. "
        f"One-sided p = (1 + count of null scores >= observed) / (1 + shuffles). "
        f"p_block-swap on this seed is {example['p_blockswap']:.3f}.",
        fontsize=8,
        color="#333333",
    )
    _save(fig, path)


def _split_name(row: dict) -> str:
    for key in ("split", "split_id"):
        if row.get(key):
            return str(row[key])
    session = str(row.get("session_id", ""))
    match = re.search(r"split[-_ ]*([A-Za-z0-9]+)", session, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return session or "session"


def _finite(value) -> bool:
    try:
        return value is not None and bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def _load_method_results(results_dir: Path) -> list[dict]:
    rows = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict) or "method_id" not in payload or "score" not in payload:
            continue
        payload["_split"] = _split_name(payload)
        payload["_path"] = path.name
        rows.append(payload)
    return rows


def plot_real_results(results_dir, out_path=None):
    """Bar of score per method and split. Stars mark p_N1 < 0.05. Crosses mark ineligible rows.

    Returns the PNG path, or None when results_dir has no method-result JSON.
    """
    results_dir = Path(results_dir)
    rows = _load_method_results(results_dir)
    if not rows:
        print(f"plot_real_results: no method JSON in {results_dir}")
        return None

    methods = [m for m in ("M1", "M2", "M3", "M4") if any(r["method_id"] == m for r in rows)]
    extras = sorted({r["method_id"] for r in rows} - set(methods))
    methods.extend(extras)
    splits = sorted({r["_split"] for r in rows}, key=lambda s: (len(s), s))
    index = {(r["method_id"], r["_split"]): r for r in rows}

    x = np.arange(len(methods))
    width = min(0.8 / max(len(splits), 1), 0.36)
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    scores = []
    yes, ineligible = [], []
    for s_i, split in enumerate(splits):
        offset = (s_i - (len(splits) - 1) / 2) * width
        heights, positions = [], []
        for m_i, method in enumerate(methods):
            row = index.get((method, split))
            xpos = x[m_i] + offset
            if row is None:
                continue
            if row.get("eligible") and _finite(row.get("score")):
                height = float(row["score"])
                heights.append(height)
                positions.append(xpos)
                scores.append(height)
                p_value = row.get("p_n1")
                if _finite(p_value) and float(p_value) < ALPHA:
                    mark, color = "*", "#9B2226"
                    if height > 0:
                        yes.append(f"{method} split {split}")
                else:
                    mark, color = "n.s.", "#555555"
                ax.text(
                    xpos,
                    height,
                    f"{mark} {height:.3f}",
                    ha="center",
                    va="bottom" if height >= 0 else "top",
                    color=color,
                    fontsize=8,
                )
            else:
                ax.scatter([xpos], [0.0], marker="x", s=56, color="#6B2D5B", zorder=4, linewidths=1.6)
                ineligible.append(f"{method} split {split}")
        if heights:
            ax.bar(
                positions,
                heights,
                width=width * 0.92,
                color=SPLIT_COLORS[s_i % len(SPLIT_COLORS)],
                label=f"split {split}",
            )
    ax.axhline(0, color="#222222", lw=0.8)
    ax.scatter([], [], marker="x", s=46, color="#6B2D5B", label="ineligible")
    ax.plot([], [], color="#9B2226", marker="*", ls="none", label=f"p_N1 < {ALPHA:.2f}")
    if len(yes) == 1:
        title = f"Real data: only {yes[0]} is a significant positive score"
    elif yes:
        title = "Real data: significant positive scores for " + ", ".join(yes)
    else:
        title = "Real data: no method has a significant positive score"
    ax.set_title(title)
    ax.set_ylabel("score (method-specific units)")
    ax.set_xlabel("method")
    ax.set_xticks(x, methods)
    if scores:
        lo, hi = min(scores + [0.0]), max(scores + [0.0])
        span = max(hi - lo, 0.02)
        ax.set_ylim(lo - 0.25 * span, hi + 0.45 * span)
    _style(ax)
    ax.legend(frameon=False, fontsize=9, loc="best")
    fig.text(
        0.01,
        -0.03,
        "Star: eligible and p_N1 < 0.05. n.s.: eligible and not significant. "
        "Cross: the method's requirement check failed, so there is no score. "
        "Source: results/real.",
        fontsize=8,
        color="#333333",
    )
    out = Path(out_path) if out_path is not None else FIG / "real_scores.png"
    _save(fig, out)
    return out


def main() -> None:
    np.random.seed(SEED)
    t0 = time.perf_counter()
    FIG.mkdir(parents=True, exist_ok=True)
    print("eigenvalue spectrum")
    plot_eigenvalue_bounds(FIG / "eigenvalue_bounds.png")
    print(f"controls, {N_SEEDS} seeds")
    rates, example = control_rates(AssemblyParams(n_shuffles=N_SHUFFLES))
    plot_controls(rates, FIG / "controls_m3_m4.png")
    plot_reactivation(example, FIG / "reactivation_strength_example.png")
    plot_null(example, FIG / "null_distribution_example.png")
    if REAL.is_dir() and any(REAL.glob("*.json")):
        plot_real_results(REAL)
    print(f"done in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
