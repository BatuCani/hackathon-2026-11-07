"""Positive / negative control runs for the method tests (plans/engineer-b.md section 6).

Zixi's verdict rule calls `run_controls` when a method says "no" or methods disagree
(research/team-brief.md section 2 diagram: "counts only if tests pass").
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import m3_pca, m4_ica
from .assemblies import AssemblyParams
from .contract import Recording
from .synth import make_session

RUNNERS = {"M3": m3_pca.run, "M4": m4_ica.run}
NEGATIVES = ("no_sleep_coactivity", "pre_existing", "other_assemblies")


def _assemblies(n_cells: int, k: int = 3, size: int = 8, offset: int = 0) -> list[np.ndarray]:
    return [np.arange(offset + j * size, offset + (j + 1) * size) for j in range(k)]


def scenario(
    name: str,
    *,
    seed: int,
    tau_s: float = 1.0,
    n_cells: int = 50,
    fs: float = 10.0,
    frames: dict | None = None,
    nrem_fraction: float = 0.7,
    size: int = 8,
) -> Recording:
    """Synthetic sessions of plan section 5 (default: N=50, fs=10 Hz, 3 assemblies of 8 cells, TASK p=0.02).

    positive            PRE 0,     POST 0.005           (T-M3-1)
    no_sleep_coactivity PRE 0,     POST 0               (T-M3-2)
    pre_existing        PRE 0.005, POST 0.005           (T-M3-3)
    other_assemblies    PRE 0,     POST 0.005 on other cells (T-M3-4)
    noise_only          no assemblies at all            (T-M3-5)
    reversed            PRE 0.005, POST 0               (T-M3-8)
    """
    p = {
        "positive": (0.0, 0.005),
        "no_sleep_coactivity": (0.0, 0.0),
        "pre_existing": (0.005, 0.005),
        "other_assemblies": (0.0, 0.005),
        "noise_only": (0.0, 0.0),
        "reversed": (0.005, 0.0),
    }[name]
    task = [] if name == "noise_only" else _assemblies(n_cells, size=size)
    sleep = _assemblies(n_cells, size=size, offset=3 * size) if name == "other_assemblies" else None
    return make_session(
        n_cells=n_cells, fs=fs, frames=frames, nrem_fraction=nrem_fraction,
        assemblies=task, sleep_assemblies=sleep,
        p_activation={"PRE": p[0], "TASK": 0.02, "POST": p[1]},
        tau_s=tau_s, seed=seed, session_id=f"control-{name}-{seed}",
    )


@dataclass(frozen=True)
class ControlReport:
    method_id: str
    tpr: float
    fpr: dict[str, float]
    passed: bool
    thresholds: dict
    n_seeds: int = 0
    matched: dict = field(default_factory=dict)


def _median_lag1(X: np.ndarray) -> float:
    Xc = X - X.mean(axis=1, keepdims=True)
    den = np.sum(Xc * Xc, axis=1)
    ok = den > 0
    return float(np.median(np.sum(Xc[ok, :-1] * Xc[ok, 1:], axis=1) / den[ok]))


def run_controls(
    method_id: str,
    like: Recording,
    *,
    seed: int,
    n_seeds: int = 20,
    params: AssemblyParams | None = None,
    alpha: float = 0.05,
    min_tpr: float = 0.9,
    max_fpr: float = 0.1,
) -> ControlReport:
    """Synthetic sessions matched to `like` (n_cells, frames per epoch, fs, NREM fraction, median lag-1
    autocorrelation); positive = planted reactivation, negatives = T-M3-2, -3, -4 scenarios.

    A run counts as "yes" if eligible, score > 0, p_n1 < alpha and p_blockswap < alpha
    (the plan's recommended rule: require both p-values; [TEAM DECISION for Zixi]).
    thresholds min_tpr / max_fpr are [PROPOSAL]s.
    """
    run = RUNNERS[method_id]
    params = params or AssemblyParams()
    n_cells = like.deconv.shape[0]
    frames = {ep: int(np.sum(like.epoch == ep)) for ep in ("PRE", "TASK", "POST")}
    sleep = np.isin(like.epoch, ["PRE", "POST"])
    nrem_fraction = float(np.mean(like.sleep_stage[sleep] == "NREM")) if sleep.any() else 0.7
    a = _median_lag1(like.deconv)
    tau_s = float(-1.0 / (like.fs * np.log(a))) if 0 < a < 1 else 0.0
    size = max(2, min(8, n_cells // 6))
    matched = {"n_cells": n_cells, "frames": frames, "fs": like.fs, "nrem_fraction": nrem_fraction,
               "median_lag1": a, "tau_s": tau_s, "assembly_size": size}

    def yes_rate(name: str) -> float:
        hits = 0
        for s in range(n_seeds):
            rec = scenario(name, seed=seed * 1000 + s, tau_s=tau_s, n_cells=n_cells, fs=like.fs,
                           frames=frames, nrem_fraction=nrem_fraction, size=size)
            r = run(rec, seed=seed * 1000 + s, params=params)
            hits += bool(r.eligible and r.score > 0 and r.p_n1 < alpha and r.details["p_blockswap"] < alpha)
        return hits / n_seeds

    negatives = [n for n in NEGATIVES if n != "other_assemblies" or n_cells >= 6 * size]
    tpr = yes_rate("positive")
    fpr = {name: yes_rate(name) for name in negatives}
    passed = tpr >= min_tpr and all(v <= max_fpr for v in fpr.values())
    thresholds = {"alpha": alpha, "min_tpr": min_tpr, "max_fpr": max_fpr, "rule": "score>0 & p_n1<alpha & p_blockswap<alpha"}
    return ControlReport(method_id, tpr, fpr, passed, thresholds, n_seeds, matched)
