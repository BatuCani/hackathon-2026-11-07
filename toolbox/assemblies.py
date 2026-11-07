"""Shared assembly machinery for M3 (PCA) and M4 (ICA) (plans/engineer-b.md Steps 2-3).

Math from research/team-brief.md section 4 and research/source-of-truth.md
("Shared preprocessing", M4, M5, M6). Implemented from the equations; no GPL code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

import numpy as np

from .contract import MethodResult, Recording, Requirement, analysis_mask
from .nulls import circular_shift, n1_offsets, n1_pvalue, rng_for

EPOCHS = ("PRE", "TASK", "POST")


@dataclass(frozen=True)
class AssemblyParams:
    n_shuffles: int = 500  # [brief]
    bound_quantile: float = 0.95  # [TEAM DECISION], SoT gap 2
    min_shift: int = 1  # [TEAM DECISION]
    bin_frames: int = 1  # [TEAM DECISION], SoT gap 5
    min_cells: int = 10  # [TEAM DECISION], SoT gap 7
    min_task_frames_per_cell: int = 5  # [TEAM DECISION]: B_task >= 5 * N
    min_sleep_frames: int = 300  # [TEAM DECISION]: per PRE and POST NREM
    ddof: int = 0  # SoT shared preprocessing: 1/B form
    blockswap_s: float = 20.0  # [TEAM DECISION], plan Step 3 limitation: 20 s blocks
    alpha: float = 0.05  # [TEAM DECISION], reported only; the verdict rule is Zixi's


# ---- linear algebra ---------------------------------------------------------------------------


def zscore(X: np.ndarray, ddof: int = 0) -> np.ndarray:
    """Row-wise z-score (population sd by default, matching C = Z Z^T / B)."""
    return (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, ddof=ddof, keepdims=True)


def correlation(Z: np.ndarray) -> np.ndarray:
    """C = Z Z^T / B, (N, N). SoT writes Z^T Z; the intended object is N x N (SoT notes)."""
    return Z @ Z.T / Z.shape[1]


def eigh_desc(C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues descending; eigenvector signs fixed so the largest-|v| entry is positive."""
    w, V = np.linalg.eigh(C)
    w, V = w[::-1], V[:, ::-1]
    signs = np.sign(V[np.argmax(np.abs(V), axis=0), np.arange(V.shape[1])])
    return w, V * np.where(signs == 0, 1.0, signs)


def projector(v: np.ndarray) -> np.ndarray:
    """P = v v^T with diagonal set to 0 (SoT A06)."""
    P = np.outer(v, v)
    np.fill_diagonal(P, 0.0)
    return P


def reactivation_strength(V: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """(K, B): R_k(t) = z(t)^T P_k z(t) = (v_k . z(t))^2 - sum_i v_ki^2 z_i(t)^2."""
    return (V.T @ Z) ** 2 - (V**2).T @ (Z**2)


def mean_strength(V: np.ndarray, Z: np.ndarray) -> np.ndarray:
    """(K,): time average of R_k; equals v^T C v - ||v||^2 when rows of Z are z-scored (ddof=0)."""
    B = Z.shape[1]
    return np.sum((V.T @ Z) ** 2, axis=1) / B - (V**2).T @ np.mean(Z**2, axis=1)


# ---- N1 eigenvalue bound ----------------------------------------------------------------------


@dataclass(frozen=True)
class EigenBound:
    bound: float  # N1 bound
    null_max_eigs: np.ndarray  # (n_shuffles,), largest eigenvalue per shuffle
    mp_bound: float  # analytical bound, reported for comparison only
    quantile: float


def n1_eigen_bound(
    Z_task: np.ndarray, *, n_shuffles: int = 500, quantile: float = 0.95, rng: np.random.Generator, min_shift: int = 1
) -> EigenBound:
    """Bound = quantile of the per-shuffle largest eigenvalue of the N1-shifted TASK correlation matrix.

    Circular shift keeps each row's values, so the z-scored matrix is shifted directly.
    mp_bound = (1 + sqrt(N/B))^2 (research/briefing.md section 2, "not verbatim"): never used for selection.
    """
    N, B = Z_task.shape
    offsets = n1_offsets(N, B, n_shuffles, rng, min_shift)
    null_max = np.array([np.linalg.eigvalsh(correlation(circular_shift(Z_task, o)))[-1] for o in offsets])
    return EigenBound(
        bound=float(np.quantile(null_max, quantile)),
        null_max_eigs=null_max,
        mp_bound=float((1 + np.sqrt(N / B)) ** 2),
        quantile=quantile,
    )


# ---- requirement check and significant subspace -----------------------------------------------


def _rebin(X: np.ndarray, mask: np.ndarray, k: int) -> np.ndarray:
    """Select masked frames; for k > 1 sum within contiguous runs of the mask, dropping remainders."""
    if k == 1:
        return X[:, mask]
    m = np.concatenate([[False], mask, [False]]).astype(np.int8)
    starts, ends = np.flatnonzero(np.diff(m) == 1), np.flatnonzero(np.diff(m) == -1)
    cols = []
    for s, e in zip(starts, ends):
        n = (e - s) // k
        if n:
            cols.append(X[:, s : s + n * k].reshape(X.shape[0], n, k).sum(axis=2))
    return np.concatenate(cols, axis=1) if cols else X[:, :0]


@dataclass(frozen=True)
class Subspace:
    kept_cells: np.ndarray  # indices into rec.cell_id
    dropped_cells: np.ndarray  # indices into rec.cell_id (zero variance in some epoch)
    eigvals: np.ndarray  # TASK correlation eigenvalues, descending
    V_sig: np.ndarray  # (N_kept, n_sig)
    n_sig: int
    bound: EigenBound
    Z: dict  # "PRE", "TASK", "POST" z-scored analysis matrices
    fs_bins: float  # sampling rate of the analysis bins, Hz


def significant_subspace(rec: Recording, params: AssemblyParams, seed: int) -> Subspace | Requirement:
    """Shared by M3 and M4 (same rng stream "eigen_bound", so both agree on n_sig).

    Returns a Requirement (eligible=False) when the data minima fail; otherwise a Subspace,
    possibly with n_sig = 0 (each method applies its own component minimum).
    """
    n_bad = int(np.size(rec.deconv) - np.isfinite(rec.deconv).sum())
    if n_bad:
        return Requirement(False, f"deconv has {n_bad} non-finite values", ("finite deconv values",))

    X = {ep: _rebin(rec.deconv, analysis_mask(rec, ep), params.bin_frames) for ep in EPOCHS}
    for ep in ("PRE", "POST"):
        n = X[ep].shape[1]
        if n < params.min_sleep_frames:
            return Requirement(
                False,
                f"{ep} NREM frames {n} < {params.min_sleep_frames}",
                (f"{ep} NREM frames >= {params.min_sleep_frames}",),
            )
    if X["TASK"].shape[1] == 0:
        return Requirement(False, "TASK frames 0", (f"TASK frames >= {params.min_task_frames_per_cell} per cell",))

    zero_var = np.zeros(rec.deconv.shape[0], dtype=bool)
    for ep in EPOCHS:
        zero_var |= X[ep].std(axis=1) == 0
    kept, dropped = np.flatnonzero(~zero_var), np.flatnonzero(zero_var)
    N = kept.size
    if N < params.min_cells:
        return Requirement(
            False,
            f"{N} cells < {params.min_cells} (after dropping {dropped.size} zero-variance cells)",
            (f"cells >= {params.min_cells}",),
        )
    B_task = X["TASK"].shape[1]
    need = params.min_task_frames_per_cell * N
    if B_task < need:
        return Requirement(
            False,
            f"TASK frames {B_task} < {need} ({params.min_task_frames_per_cell} per cell x {N} cells)",
            (f"TASK frames >= {need}",),
        )

    Z = {ep: zscore(X[ep][kept], params.ddof) for ep in EPOCHS}
    bound = n1_eigen_bound(
        Z["TASK"],
        n_shuffles=params.n_shuffles,
        quantile=params.bound_quantile,
        rng=rng_for(seed, rec.session_id, "eigen_bound"),
        min_shift=params.min_shift,
    )
    eigvals, V = eigh_desc(correlation(Z["TASK"]))
    n_sig = int(np.sum(eigvals > bound.bound))
    return Subspace(kept, dropped, eigvals, V[:, :n_sig], n_sig, bound, Z, rec.fs / params.bin_frames)


# ---- strength test: N1 p-value and block-swap p-value -----------------------------------------


def _blocks(R: np.ndarray, L: int) -> tuple[np.ndarray, np.ndarray]:
    """Cut R (K, B) into consecutive blocks of L frames (last partial block kept): sums (K, nb), lengths (nb,)."""
    edges = np.arange(0, R.shape[1], L)
    return np.add.reduceat(R, edges, axis=1), np.diff(np.append(edges, R.shape[1]))


def strength_test(W: np.ndarray, sub: Subspace, params: AssemblyParams, *, seed: int, session_id: str) -> dict:
    """Score = mean over components of (mean R in POST - mean R in PRE); templates W fixed from TASK.

    p_n1: N1 applied independently to Z_PRE and Z_POST, n_shuffles times.
    p_blockswap: PRE and POST R(t) cut into blockswap_s blocks, block labels permuted n_shuffles times.
    """
    Zpre, Zpost = sub.Z["PRE"], sub.Z["POST"]
    mR_pre, mR_post = mean_strength(W, Zpre), mean_strength(W, Zpost)
    delta = mR_post - mR_pre
    score = float(delta.mean())

    rng = rng_for(seed, session_id, "n1_strength")
    off_pre = n1_offsets(*Zpre.shape, params.n_shuffles, rng, params.min_shift)
    off_post = n1_offsets(*Zpost.shape, params.n_shuffles, rng, params.min_shift)
    null_pre = np.array([mean_strength(W, circular_shift(Zpre, o)).mean() for o in off_pre])
    null_post = np.array([mean_strength(W, circular_shift(Zpost, o)).mean() for o in off_post])
    null_score = null_post - null_pre

    L = max(1, int(round(params.blockswap_s * sub.fs_bins)))
    S_pre, L_pre = _blocks(reactivation_strength(W, Zpre), L)
    S_post, L_post = _blocks(reactivation_strength(W, Zpost), L)
    S, lens = np.concatenate([S_pre, S_post], axis=1), np.concatenate([L_pre, L_post])
    n_post = S_post.shape[1]
    rng_bs = rng_for(seed, session_id, "blockswap")
    null_bs = np.empty(params.n_shuffles)
    for s in range(params.n_shuffles):
        perm = rng_bs.permutation(lens.size)
        post, pre = perm[:n_post], perm[n_post:]
        null_bs[s] = np.mean(S[:, post].sum(1) / lens[post].sum() - S[:, pre].sum(1) / lens[pre].sum())

    return {
        "score": score,
        "p_n1": n1_pvalue(score, null_score),
        "delta_k": delta,
        "mean_R_pre": mR_pre,
        "mean_R_post": mR_post,
        "p_n1_post_alone": n1_pvalue(float(mR_post.mean()), null_post),
        "p_n1_pre_alone": n1_pvalue(float(mR_pre.mean()), null_pre),
        "p_blockswap": n1_pvalue(score, null_bs),
        "blockswap_frames": L,
        "null_n1_quantiles": np.quantile(null_score, [0.05, 0.5, 0.95]),
    }


# ---- shared method runner (M3 and M4 differ only in the weights and the component minimum) ----


def run_assembly_method(
    rec: Recording,
    *,
    method_id: str,
    seed: int,
    params: AssemblyParams,
    min_sig: int,
    weights: Callable[[Subspace], np.ndarray | Requirement],
    extra_params: dict | None = None,
) -> tuple[MethodResult, dict | None]:
    """Returns (MethodResult, traces) where traces holds R(t) on PRE and POST for the demo plot."""
    all_params = {**asdict(params), **(extra_params or {})}

    def ineligible(req: Requirement, details: dict) -> tuple[MethodResult, None]:
        res = MethodResult(
            method_id, rec.session_id, False, req.reason, float("nan"), float("nan"),
            params.n_shuffles, seed, all_params, details, tuple(req.missing),
        )
        return res, None

    sub = significant_subspace(rec, params, seed)
    if isinstance(sub, Requirement):
        return ineligible(sub, {})

    details = {
        "n_cells_kept": int(sub.kept_cells.size),
        "dropped_cells": [str(c) for c in rec.cell_id[sub.dropped_cells]],
        "n_frames": {ep: int(sub.Z[ep].shape[1]) for ep in EPOCHS},
        "eigenvalues_top10": sub.eigvals[:10],
        "bound": sub.bound.bound,
        "mp_bound": sub.bound.mp_bound,
        "n_sig": sub.n_sig,
        "n_above_mp": int(np.sum(sub.eigvals > sub.bound.mp_bound)),
    }
    if sub.n_sig < min_sig:
        lam1 = float(sub.eigvals[0])
        if min_sig == 1:
            reason = f"0 TASK components above N1 bound (lambda_1={lam1:.4f}, bound={sub.bound.bound:.4f})"
        else:
            reason = f"{sub.n_sig} < {min_sig} significant components (N1 bound={sub.bound.bound:.4f}, lambda_1={lam1:.4f})"
        need = f"at least {min_sig} TASK component{'s' if min_sig > 1 else ''} above the N1 eigenvalue bound"
        return ineligible(Requirement(False, reason, (need,)), details)

    W = weights(sub)
    if isinstance(W, Requirement):
        return ineligible(W, details)

    t = strength_test(W, sub, params, seed=seed, session_id=rec.session_id)
    details.update({k: v for k, v in t.items() if k not in ("score", "p_n1")})
    details["weights"] = W
    details["kept_cell_ids"] = [str(c) for c in rec.cell_id[sub.kept_cells]]
    res = MethodResult(
        method_id, rec.session_id, True, "", t["score"], t["p_n1"], params.n_shuffles, seed, all_params, details
    )
    traces = {
        "R_pre": reactivation_strength(W, sub.Z["PRE"]),
        "R_post": reactivation_strength(W, sub.Z["POST"]),
        "fs_bins": sub.fs_bins,
    }
    return res, traces
