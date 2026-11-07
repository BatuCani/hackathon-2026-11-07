"""Yes/no panels for M1–M4, one method per quadrant.

YES is a DANDI:000044 positive-control session (local NWB).
NO is RIKEN mouse05 split A.
Every score, null and curve comes from the toolbox. Display bins only
compress reactivation strength for the slide; they are not a second analysis.

    OMP_NUM_THREADS=1 uv run --python 3.12 --with matplotlib python scripts/plot_method_panels.py

Writes results/figures/method_panels.png.
Shuffles default to 100 (the locked key uses 500); the caption says so.
"""

from __future__ import annotations

import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from toolbox.assemblies import (  # noqa: E402
    AssemblyParams,
    correlation,
    mean_strength,
    reactivation_strength,
    zscore,
)
from toolbox.contract import analysis_mask  # noqa: E402
from toolbox.loader import load_sessions  # noqa: E402
from toolbox.loader_dandi import load_dandi44  # noqa: E402
from toolbox.m1_pair_corr import M1Params, _prepare, pair_upper, run as run_m1  # noqa: E402
from toolbox.m2_ev_rev import M2Params, pair_corr_vec, run as run_m2  # noqa: E402
from toolbox.m3_pca import run_with_traces as run_m3  # noqa: E402
from toolbox.m4_ica import run_with_traces as run_m4  # noqa: E402
from toolbox.nulls import circular_shift, n1_offsets, n1_pvalue, rng_for  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "figures" / "method_panels.png"
CACHE = Path(
    "/Users/batu/.treehouse/firstmate-7bab20/5/firstmate/data/hackathon-method-panels/payload.pkl"
)
N_SHUFFLES = 100
SEED = 0
ALPHA = 0.05
N_SHOW = 5
BINS_PER_EPOCH = 28
YES_C = "#1a7f4b"
NO_C = "#c4321f"
YES_BG = "#e8f6ee"
NO_BG = "#fdecea"

EXPLAINS = {
    "M1": "Pair correlations in TASK should match POST more than PRE. D1 is that difference; the histogram is the N1 null.",
    "M2": "EV is the TASK–POST link after PRE; REV swaps the two sleeps. Yes when EV is larger and clears the null.",
    "M3": "PCA templates come from TASK. R(t) is their strength over time; yes when POST exceeds PRE above the null.",
    "M4": "ICA de-mixes those components, then uses the same test: POST above PRE, and above the N1 null.",
}


def _yes_nwb() -> Path:
    env = os.environ.get("DANDI44_NWB")
    if env:
        return Path(env)
    root = Path("/Users/batu/hackathon-data/000044")
    achilles = sorted(root.rglob("*Achilles*.nwb"))
    if achilles:
        return achilles[0]
    buddy = sorted(p for p in root.rglob("*Buddy*.nwb") if p.is_file() and not p.is_symlink())
    if buddy:
        return buddy[0]
    raise FileNotFoundError(f"no DANDI:000044 NWB under {root}")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _epoch(rec, name: str) -> np.ndarray:
    return np.ascontiguousarray(rec.deconv[:, analysis_mask(rec, name)], dtype=np.float64)


def _equal_bins(R: np.ndarray, n_bins: int) -> np.ndarray:
    """Mean R inside equal index bins. Display only; the score uses the unbinned trace."""
    k, t = R.shape
    if t == 0:
        return np.zeros((k, 1))
    edges = np.linspace(0, t, n_bins + 1).astype(int)
    out = np.empty((k, n_bins))
    for i in range(n_bins):
        sl = R[:, edges[i] : max(edges[i + 1], edges[i] + 1)]
        out[:, i] = sl.mean(axis=1)
    return out


def _pack_time(parts: list[tuple[str, np.ndarray]]) -> dict:
    cols: list[np.ndarray] = []
    ticks: list[float] = []
    labels: list[str] = []
    cursor = 0
    width = None
    for name, R in parts:
        if width is None:
            width = R.shape[0]
        binned = _equal_bins(R, BINS_PER_EPOCH)
        if cols:
            cols.append(np.full((width, 1), np.nan))
            cursor += 1
        cols.append(binned)
        ticks.append(cursor + binned.shape[1] / 2.0)
        labels.append(name)
        cursor += binned.shape[1]
    return {"image": np.concatenate(cols, axis=1), "ticks": ticks, "labels": labels}


def _kept_index(rec, kept_ids: list[str]) -> np.ndarray:
    ids = np.asarray(rec.cell_id).astype(str)
    return np.array([int(np.flatnonzero(ids == c)[0]) for c in kept_ids])


def _strength_null(rec, W: np.ndarray, kept: np.ndarray, n: int) -> np.ndarray:
    """Same N1 stream as assemblies.strength_test ('n1_strength'), so the histogram matches p_N1."""
    Zpre = zscore(_epoch(rec, "PRE")[kept])
    Zpost = zscore(_epoch(rec, "POST")[kept])
    rng = rng_for(SEED, rec.session_id, "n1_strength")
    off_pre = n1_offsets(*Zpre.shape, n, rng, 1)
    off_post = n1_offsets(*Zpost.shape, n, rng, 1)
    null = np.empty(n)
    for i in range(n):
        post = mean_strength(W, circular_shift(Zpost, off_post[i])).mean()
        pre = mean_strength(W, circular_shift(Zpre, off_pre[i])).mean()
        null[i] = post - pre
    return null


def _m1_null(ready, n: int, session_id: str) -> np.ndarray:
    from toolbox.m1_pair_corr import _prepare_shift, _upper_shifted, vector_pearson

    task_u = pair_upper(ready.X["TASK"])
    rng = rng_for(SEED, session_id, "m1_n1")
    off_pre = n1_offsets(ready.X["PRE"].shape[0], ready.X["PRE"].shape[1], n, rng, 1)
    off_post = n1_offsets(ready.X["POST"].shape[0], ready.X["POST"].shape[1], n, rng, 1)
    pre_c, pre_inv, pre_iu = _prepare_shift(ready.X["PRE"])
    post_c, post_inv, post_iu = _prepare_shift(ready.X["POST"])
    null = np.empty(n)
    for s in range(n):
        r_post = vector_pearson(task_u, _upper_shifted(post_c, post_inv, post_iu, off_post[s]))
        r_pre = vector_pearson(task_u, _upper_shifted(pre_c, pre_inv, pre_iu, off_pre[s]))
        null[s] = r_post - r_pre
    return null


def _quantiles(null: np.ndarray) -> list[float]:
    finite = null[np.isfinite(null)]
    return [float(x) for x in np.quantile(finite, [0.05, 0.5, 0.95])]


def _assembly(rec, runner, method: str) -> dict:
    params = AssemblyParams(n_shuffles=N_SHUFFLES)
    result, traces = runner(rec, seed=SEED, params=params)
    if traces is None or not result.eligible:
        raise RuntimeError(f"{method} {rec.session_id} ineligible: {result.reason}")
    W = np.asarray(result.details["weights"], dtype=np.float64)
    kept = _kept_index(rec, result.details["kept_cell_ids"])
    n_sig = int(result.details["n_sig"])
    show = min(N_SHOW, n_sig, W.shape[1])
    R_task = reactivation_strength(W[: , :show], zscore(_epoch(rec, "TASK")[kept]))
    packed = _pack_time([
        ("PRE", traces["R_pre"][:show]),
        ("TASK", R_task),
        ("POST", traces["R_post"][:show]),
    ])
    null = _strength_null(rec, W, kept, N_SHUFFLES)
    p_check = n1_pvalue(float(result.score), null)
    if abs(p_check - float(result.p_n1)) > 1e-9:
        raise RuntimeError(f"{method} null histogram does not match run p ({p_check} vs {result.p_n1})")
    return {
        "score": float(result.score),
        "p": float(result.p_n1),
        "q": _quantiles(null),
        "null": null,
        "n_sig": n_sig,
        "shown": show,
        "image": packed["image"],
        "ticks": packed["ticks"],
        "labels": packed["labels"],
        "trace": packed["image"][0],
    }


def _one_session(rec) -> dict:
    _log(f"{rec.session_id} shape={rec.deconv.shape}")
    m1_params = M1Params(n_shuffles=N_SHUFFLES)
    m1 = run_m1(rec, seed=SEED, params=m1_params)
    if not m1.eligible:
        raise RuntimeError(f"M1 {rec.session_id} ineligible: {m1.reason}")
    ready = _prepare(rec, m1_params)
    null_m1 = _m1_null(ready, N_SHUFFLES, rec.session_id)
    p_check = n1_pvalue(float(m1.score), null_m1[np.isfinite(null_m1)])
    if abs(p_check - float(m1.p_n1)) > 1e-9:
        raise RuntimeError(f"M1 null histogram does not match run p ({p_check} vs {m1.p_n1})")
    _log(f"  M1 score={m1.score:+.4f} p={m1.p_n1:.4f}")

    m2 = run_m2(rec, seed=SEED, params=M2Params(n_shuffles=N_SHUFFLES))
    if not m2.eligible:
        raise RuntimeError(f"M2 {rec.session_id} ineligible: {m2.reason}")
    task = _epoch(rec, "TASK")
    active = task.std(axis=1) > 0
    corr = correlation(zscore(task[active]))
    _log(f"  M2 score={m2.score:+.4f} p={m2.p_n1:.4f} EV={m2.details['ev']:.4f} REV={m2.details['rev']:.4f}")

    m3 = _assembly(rec, run_m3, "M3")
    _log(f"  M3 score={m3['score']:+.4f} p={m3['p']:.4f} n_sig={m3['n_sig']}")
    m4 = _assembly(rec, run_m4, "M4")
    _log(f"  M4 score={m4['score']:+.4f} p={m4['p']:.4f} n_sig={m4['n_sig']}")

    return {
        "session_id": rec.session_id,
        "m1": {
            "score": float(m1.score),
            "p": float(m1.p_n1),
            "q": _quantiles(null_m1),
            "null": null_m1,
            "task": pair_upper(ready.X["TASK"]),
            "pre": pair_upper(ready.X["PRE"]),
            "post": pair_upper(ready.X["POST"]),
        },
        "m2": {
            "score": float(m2.score),
            "p": float(m2.p_n1),
            "ev": float(m2.details["ev"]),
            "rev": float(m2.details["rev"]),
            "corr": corr,
            "n_pairs": int(pair_corr_vec(task).size),
        },
        "m3": m3,
        "m4": m4,
    }


def compute() -> dict:
    yes_path = _yes_nwb()
    _log(f"load YES {yes_path}")
    yes = load_dandi44(yes_path)
    _log(f"load NO RIKEN split A")
    no = load_sessions(splits=("A",))[0]
    payload = {
        "n_shuffles": N_SHUFFLES,
        "seed": SEED,
        "yes_path": str(yes_path),
        "yes": _one_session(yes),
        "no": _one_session(no),
    }
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE.open("wb") as fh:
        pickle.dump(payload, fh)
    _log(f"cached {CACHE}")
    return payload


def _passes(block: dict) -> bool:
    return block["score"] > 0 and block["p"] < ALPHA


def _fmt_p(p: float) -> str:
    if p >= 0.995:
        return "1.00"
    return f"{p:.3f}"


def _rule(name: str, block: dict) -> str:
    score, p = block["score"], block["p"]
    srel = "> 0" if score > 0 else "≤ 0"
    prel = "< 0.05" if p < ALPHA else "≥ 0.05"
    word = "YES" if _passes(block) else "NO"
    return f"{word}: {name} = {score:+.3f} ({srel}), p_N1 = {_fmt_p(p)} ({prel})"


def _paint(ax, color: str, bg: str) -> None:
    ax.set_facecolor(bg)
    for spine in ax.spines.values():
        spine.set_color(color)
        spine.set_linewidth(1.3)


def _scatter(ax, block: dict, color: str, bg: str, limits: tuple[float, float]) -> None:
    rng = np.random.default_rng(0)
    n = block["task"].size
    take = rng.choice(n, size=min(1800, n), replace=False)
    x = block["task"][take]
    ax.scatter(x, block["pre"][take], s=6, c="#98a2b3", alpha=0.35, linewidths=0, label="PRE", rasterized=True)
    ax.scatter(x, block["post"][take], s=6, c=color, alpha=0.4, linewidths=0, label="POST", rasterized=True)
    lo, hi = limits
    ax.plot([lo, hi], [lo, hi], color="#98a2b3", lw=0.7, zorder=0)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel("TASK pair r", fontsize=7)
    ax.set_ylabel("sleep pair r", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ax.legend(frameon=True, framealpha=0.88, edgecolor="none", fontsize=6.5, loc="upper left", markerscale=2)
    _paint(ax, color, bg)


def _null_hist(ax, null: np.ndarray, score: float, color: str, bg: str, xlabel: str) -> None:
    finite = null[np.isfinite(null)]
    ax.hist(finite, bins=16, color="#d5dbe3", edgecolor="white", linewidth=0.4)
    ax.axvline(score, color=color, lw=1.8)
    ax.set_xlabel(xlabel, fontsize=7, labelpad=1)
    ax.set_ylabel("")
    ax.tick_params(labelsize=6.5, pad=1)
    _paint(ax, color, bg)


def _offdiag_clim(corr: np.ndarray) -> tuple[float, float]:
    shown = corr.copy()
    np.fill_diagonal(shown, np.nan)
    span = float(np.nanquantile(np.abs(shown), 0.98))
    span = max(span, 0.05)
    return -span, span


def _sleep_vlim(image: np.ndarray) -> tuple[float, float]:
    """Color scale from PRE and POST only, so the TASK peak does not flatten sleep."""
    n = BINS_PER_EPOCH
    sleep = np.concatenate([image[:, :n], image[:, 2 * n + 2 :]], axis=1)
    vals = sleep[np.isfinite(sleep)]
    lo, hi = np.quantile(vals, [0.05, 0.95])
    if hi <= lo:
        hi = lo + 1e-3
    return float(lo), float(hi)


def _split_pair(fig, rect):
    """Two axes side by side inside a figure-fraction rectangle."""
    x, y, w, h = rect
    gap = 0.012
    aw = (w - gap) / 2
    return fig.add_axes([x, y, aw, h]), fig.add_axes([x + aw + gap, y, aw, h])


def _draw_m1(fig, rect, block, color, bg, limits) -> None:
    ax_s, ax_h = _split_pair(fig, rect)
    _scatter(ax_s, block, color, bg, limits)
    _null_hist(ax_h, block["null"], block["score"], color, bg, "D1")
    ax_s.set_title("pair correlation", loc="left", fontsize=8, color=color, pad=2)
    ax_h.set_title("score vs N1 null", loc="left", fontsize=8, color=color, pad=2)


def _draw_m2(fig, rect, block, color, bg, ylim) -> None:
    ax_c, ax_b = _split_pair(fig, rect)
    shown = block["corr"].copy()
    np.fill_diagonal(shown, np.nan)
    lo, hi = _offdiag_clim(block["corr"])
    cmap = plt.get_cmap("coolwarm").copy()
    cmap.set_bad("#f2f4f7")
    ax_c.imshow(np.ma.masked_invalid(shown), cmap=cmap, vmin=lo, vmax=hi, interpolation="nearest", aspect="auto")
    ax_c.set_xticks([])
    ax_c.set_yticks([])
    ax_c.set_xlabel("cells", fontsize=7, labelpad=1)
    ax_c.set_ylabel("cells", fontsize=7, labelpad=1)
    ax_c.set_title("TASK correlation", loc="left", fontsize=8, color=color, pad=2)
    _paint(ax_c, color, bg)
    values = [block["ev"], block["rev"]]
    ax_b.bar([0, 1], values, color=["#3b6fb6", "#d9822b"], width=0.72)
    ax_b.set_xticks([0, 1], ["EV", "REV"], fontsize=7)
    ax_b.set_ylim(ylim)
    ax_b.axhline(0, color="#344054", lw=0.6)
    for i, val in enumerate(values):
        ax_b.text(i, val + 0.03 * (ylim[1] - ylim[0]), f"{val:.3f}", ha="center", va="bottom", fontsize=7, color="#101828")
    ax_b.tick_params(labelsize=6.5, pad=1)
    ax_b.set_title("EV vs REV", loc="left", fontsize=8, color=color, pad=2)
    _paint(ax_b, color, bg)


def _draw_strength(fig, rect, block, color, bg, score_name: str) -> None:
    x, y, w, h = rect
    gap = 0.016
    left_w = (w - gap) * 0.58
    right_w = (w - gap) * 0.42
    ax_h = fig.add_axes([x, y, left_w, h])
    vgap = 0.040
    rh = (h - vgap) / 2
    ax_t = fig.add_axes([x + left_w + gap, y + rh + vgap, right_w, rh])
    ax_n = fig.add_axes([x + left_w + gap, y, right_w, rh])
    image = block["image"]
    lo, hi = _sleep_vlim(image)
    cmap = plt.get_cmap("magma").copy()
    cmap.set_bad("#ffffff")
    ax_h.imshow(np.ma.masked_invalid(image), cmap=cmap, vmin=lo, vmax=hi, aspect="auto", interpolation="nearest")
    ax_h.set_yticks(range(image.shape[0]))
    ax_h.set_yticklabels([str(i + 1) for i in range(image.shape[0])], fontsize=6)
    ax_h.set_xticks(block["ticks"])
    ax_h.set_xticklabels(block["labels"], fontsize=6.5)
    ax_h.set_ylabel("component", fontsize=7, labelpad=1)
    ax_h.tick_params(labelsize=6, pad=1)
    shown = block["shown"]
    extra = f", {shown} of {block['n_sig']}" if block["n_sig"] > shown else f", {block['n_sig']}"
    ax_h.set_title("R(t)" + extra, loc="left", fontsize=8, color=color, pad=2)
    _paint(ax_h, color, bg)

    n = BINS_PER_EPOCH
    pre, post = block["trace"][:n], block["trace"][2 * n + 2 :]
    ax_t.plot(np.arange(n), pre, color=color, lw=1.15)
    ax_t.plot(np.arange(n + 4, 2 * n + 4), post, color=color, lw=1.15)
    ax_t.set_xticks([n / 2, n + 4 + n / 2])
    ax_t.set_xticklabels(["PRE", "POST"], fontsize=6.5)
    sleep = np.concatenate([pre, post])
    sleep = sleep[np.isfinite(sleep)]
    pad = 0.12 * (sleep.max() - sleep.min() + 1e-6)
    ax_t.set_ylim(float(sleep.min() - pad), float(sleep.max() + pad))
    ax_t.tick_params(labelsize=6, pad=1)
    ax_t.set_title("component 1, sleep", loc="left", fontsize=8, color=color, pad=2)
    _paint(ax_t, color, bg)

    _null_hist(ax_n, block["null"], block["score"], color, bg, score_name)
    ax_n.set_title("score vs N1 null", loc="left", fontsize=8, color=color, pad=2)


def _m1_limits(payload: dict) -> tuple[float, float]:
    flat = np.concatenate([
        payload[s]["m1"][k] for s in ("yes", "no") for k in ("task", "pre", "post")
    ])
    flat = flat[np.isfinite(flat)]
    lo, hi = np.quantile(flat, [0.01, 0.99])
    pad = 0.08 * (hi - lo + 1e-6)
    return float(lo - pad), float(hi + pad)


def _m2_ylim(payload: dict) -> tuple[float, float]:
    vals = [payload[s]["m2"][k] for s in ("yes", "no") for k in ("ev", "rev")]
    span = max(abs(min(vals)), abs(max(vals)), 0.02)
    return -0.12 * span, span * 1.45


def _banner(fig, rect, tag: str, label: str, color: str) -> None:
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, color=color, lw=0, clip_on=False))
    ax.text(0.03, 0.64, tag, color="white", fontsize=8.5, fontweight="bold", va="center", ha="left")
    ax.text(0.03, 0.28, label, color="white", fontsize=7, va="center", ha="left")


def plot(payload: dict) -> None:
    m1_lim = _m1_limits(payload)
    m2_ylim = _m2_ylim(payload)
    yes_id = payload["yes"]["session_id"]
    no_id = payload["no"]["session_id"]

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.linewidth": 0.6,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.titlepad": 2,
    })
    fig = plt.figure(figsize=(17.2, 13.2))
    # Explicit rectangles, in figure fractions, so labels cannot collapse onto each other.
    panels = [
        ("M1  cell-pair correlation", "m1", (0.055, 0.55, 0.43, 0.41)),
        ("M2  EV / REV", "m2", (0.545, 0.55, 0.43, 0.41)),
        ("M3  PCA reactivation strength", "m3", (0.055, 0.085, 0.43, 0.41)),
        ("M4  ICA reactivation strength", "m4", (0.545, 0.085, 0.43, 0.41)),
    ]
    score_name = {"m1": "D1", "m2": "D2", "m3": "D3", "m4": "D4"}
    for title, key, (x, y, w, h) in panels:
        fig.text(x, y + h - 0.004, title, ha="left", va="top", fontsize=13, fontweight="bold", color="#101828")
        half_gap = 0.012
        hw = (w - half_gap) / 2
        banner_h = 0.032
        banner_y = y + h - 0.058
        plot_y = y + 0.100
        plot_h = banner_y - plot_y - 0.030
        for i, (side, color, bg, tag) in enumerate((
            ("yes", YES_C, YES_BG, "YES — reactivation detected"),
            ("no", NO_C, NO_BG, "NO — no reactivation"),
        )):
            hx = x + i * (hw + half_gap)
            label = yes_id if side == "yes" else no_id
            block = payload[side][key]
            _banner(fig, [hx, banner_y, hw, banner_h], tag, label, color)
            rect = (hx, plot_y, hw, plot_h)
            if key == "m1":
                _draw_m1(fig, rect, block, color, bg, m1_lim)
            elif key == "m2":
                _draw_m2(fig, rect, block, color, bg, m2_ylim)
            else:
                _draw_strength(fig, rect, block, color, bg, score_name[key])
            fig.text(hx + hw / 2, plot_y - 0.048, _rule(score_name[key], block),
                     ha="center", va="top", fontsize=7.3, color=color)
        fig.text(x, y + 0.006, EXPLAINS[key.upper()], ha="left", va="bottom", fontsize=8, color="#344054")

    fig.text(
        0.5, 0.034,
        f"Toolbox M1–M4, seed {SEED}, {N_SHUFFLES} N1 circular shifts "
        f"(the locked key uses 500; smallest p here is 1/{N_SHUFFLES + 1:.0f}).  OMP_NUM_THREADS=1.",
        ha="center", va="center", fontsize=8, color="#475467",
    )
    fig.text(
        0.5, 0.014,
        f"YES: DANDI:000044 {yes_id}.   NO: RIKEN {no_id}.   "
        "Heatmap color is scaled on PRE and POST; TASK is brighter when it exceeds that scale. Bins are display-only.",
        ha="center", va="center", fontsize=8, color="#475467",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    plt.close(fig)
    _log(f"wrote {OUT}")


def main() -> None:
    if "--plot-only" in sys.argv:
        with CACHE.open("rb") as fh:
            payload = pickle.load(fh)
        _log(f"plot-only from {CACHE}")
    else:
        payload = compute()
    for side in ("yes", "no"):
        block = payload[side]
        for key in ("m1", "m2", "m3", "m4"):
            ok = _passes(block[key])
            _log(f"{side} {key} {'YES' if ok else 'NO'} score={block[key]['score']:+.4f} p={block[key]['p']:.4f}")
    plot(payload)


if __name__ == "__main__":
    main()
