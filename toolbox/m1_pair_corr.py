"""M1 cell-pair correlation (owner: Engineer A).

Key D1 = r(C_TASK, C_POST) - r(C_TASK, C_PRE) on the flattened upper triangles
of the cell-pair Pearson matrices (PROBLEM.md). Diagonal excluded, so each
vector has N(N-1)/2 pairs.

p_n1 is the one-sided N1 p-value from toolbox.nulls: each shuffle circular-shifts
the PRE trace and the POST trace independently, per neuron, and recomputes D1.
TASK stays fixed. Stream: rng_for(seed, session_id, "m1_n1").
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .contract import MethodResult, Recording, Requirement, analysis_mask
from .nulls import circular_shift, n1_offsets, n1_pvalue, rng_for

METHOD_ID = "M1"
EPOCHS = ("PRE", "TASK", "POST")
N1_PURPOSE = "m1_n1"


@dataclass(frozen=True)
class M1Params:
    n_shuffles: int = 500
    min_sleep_frames: int = 300
    min_cells: int = 3  # two pairs; Pearson r of a single pair is undefined
    min_shift: int = 1


@dataclass(frozen=True)
class _Ready:
    X: dict
    kept: np.ndarray
    dropped: np.ndarray
    n_frames: dict


def pair_upper(X: np.ndarray) -> np.ndarray:
    """Flattened strict upper triangle of the Pearson correlation matrix of rows of X.

    Rows are L2-normalised after centering, so this matches ``np.corrcoef`` and
    does not call it (the null loop runs hundreds of times).
    """
    X = np.asarray(X, dtype=np.float64)
    Xc = X - X.mean(axis=1, keepdims=True)
    sd = np.sqrt(np.einsum("ij,ij->i", Xc, Xc))
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = Xc / sd[:, None]
    return (Z @ Z.T)[np.triu_indices(X.shape[0], k=1)]


def vector_pearson(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson r of two pair vectors. nan if either has zero variance or fewer than 2 pairs."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size != a.size:
        return float("nan")
    ac = a - a.mean()
    bc = b - b.mean()
    den = np.sqrt(np.dot(ac, ac) * np.dot(bc, bc))
    if not np.isfinite(den) or den == 0.0:
        return float("nan")
    return float(np.dot(ac, bc) / den)


def _prepare_shift(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[np.ndarray, np.ndarray]]:
    """Centered traces, per-cell inverse L2 norm, and the strict-upper index. Shift-invariant."""
    Xc = np.asarray(X, dtype=np.float64)
    Xc = Xc - Xc.mean(axis=1, keepdims=True)
    sd = np.sqrt(np.einsum("ij,ij->i", Xc, Xc))
    return Xc, 1.0 / sd, np.triu_indices(X.shape[0], k=1)


def _upper_shifted(Xc: np.ndarray, inv_sd: np.ndarray, iu: tuple[np.ndarray, np.ndarray], offset: np.ndarray) -> np.ndarray:
    Z = circular_shift(Xc, offset) * inv_sd[:, None]
    return (Z @ Z.T)[iu]


def _params(params: M1Params | None) -> M1Params:
    return M1Params() if params is None else params


def _prepare(rec: Recording, params: M1Params) -> _Ready | Requirement:
    if getattr(rec.deconv, "ndim", 0) != 2:
        return Requirement(False, "deconv must have shape (n_cells, n_frames)", ("deconv (n_cells, n_frames)",))
    n_cells, n_frames = rec.deconv.shape
    if rec.epoch.shape != (n_frames,) or rec.sleep_stage.shape != (n_frames,):
        return Requirement(
            False,
            "epoch and sleep_stage must have one label per frame",
            ("epoch and sleep_stage aligned to frames",),
        )
    n_bad = int(np.size(rec.deconv) - np.isfinite(rec.deconv).sum())
    if n_bad:
        return Requirement(False, f"deconv has {n_bad} non-finite values", ("finite deconv values",))

    ids = np.asarray(rec.cell_id)
    if ids.shape != (n_cells,):
        return Requirement(
            False,
            f"cell_id length {getattr(ids, 'size', 0)} != {n_cells} cells",
            ("same cells in PRE, TASK, POST",),
        )
    n_unique = int(np.unique(ids.astype(str)).size)
    if n_unique != n_cells:
        return Requirement(
            False,
            f"cell_id has {n_unique} unique ids for {n_cells} rows; PRE, TASK and POST must be the same cells",
            ("same cells in PRE, TASK, POST",),
        )

    n_frames_ep = {ep: int(analysis_mask(rec, ep).sum()) for ep in EPOCHS}
    for ep in ("PRE", "POST"):
        n = n_frames_ep[ep]
        if n < params.min_sleep_frames:
            return Requirement(
                False,
                f"{ep} NREM frames {n} < {params.min_sleep_frames}",
                (f"{ep} NREM frames >= {params.min_sleep_frames}",),
            )
    if n_frames_ep["TASK"] < 2:
        return Requirement(False, f"TASK frames {n_frames_ep['TASK']} < 2", ("TASK frames >= 2",))

    X = {ep: np.ascontiguousarray(rec.deconv[:, analysis_mask(rec, ep)], dtype=np.float64) for ep in EPOCHS}
    zero = np.zeros(n_cells, dtype=bool)
    for ep in EPOCHS:
        zero |= X[ep].std(axis=1) == 0
    kept = np.flatnonzero(~zero)
    if kept.size < params.min_cells:
        return Requirement(
            False,
            f"{int(kept.size)} cells < {params.min_cells} after dropping {int(zero.sum())} zero-variance cells",
            (f"at least {params.min_cells} cells with variance in PRE, TASK and POST",),
        )
    return _Ready({ep: X[ep][kept] for ep in EPOCHS}, kept, np.flatnonzero(zero), n_frames_ep)


def check_requirements(rec: Recording, params: M1Params | None = None) -> Requirement:
    params = _params(params)
    ready = _prepare(rec, params)
    if isinstance(ready, Requirement):
        return ready
    return Requirement(True, "", ())


def _fail(rec: Recording, params: M1Params, seed: int, req: Requirement, details: dict | None = None) -> MethodResult:
    return MethodResult(
        METHOD_ID,
        rec.session_id,
        False,
        req.reason,
        float("nan"),
        float("nan"),
        params.n_shuffles,
        seed,
        asdict(params),
        details or {},
        tuple(req.missing),
    )


def _details(rec: Recording, ready: _Ready, r_post: float, r_pre: float, null: np.ndarray) -> dict:
    finite = null[np.isfinite(null)]
    quantiles = [float(x) for x in np.quantile(finite, [0.05, 0.5, 0.95])] if finite.size else []
    return {
        "r_task_post": r_post,
        "r_task_pre": r_pre,
        "n_pairs": int(ready.X["TASK"].shape[0] * (ready.X["TASK"].shape[0] - 1) // 2),
        "n_cells": int(rec.deconv.shape[0]),
        "n_cells_kept": int(ready.kept.size),
        "dropped_cells": [str(c) for c in np.asarray(rec.cell_id)[ready.dropped].astype(str)],
        "n_frames": ready.n_frames,
        "same_cells": True,
        "n_finite_nulls": int(finite.size),
        "null_n1_quantiles": quantiles,
    }


def run(rec: Recording, *, seed: int, params: M1Params | None = None) -> MethodResult:
    params = _params(params)
    ready = _prepare(rec, params)
    if isinstance(ready, Requirement):
        return _fail(rec, params, seed, ready)

    try:
        rng = rng_for(seed, rec.session_id, N1_PURPOSE)
        off_pre = n1_offsets(ready.X["PRE"].shape[0], ready.X["PRE"].shape[1], params.n_shuffles, rng, params.min_shift)
        off_post = n1_offsets(
            ready.X["POST"].shape[0], ready.X["POST"].shape[1], params.n_shuffles, rng, params.min_shift
        )
    except ValueError as exc:
        return _fail(rec, params, seed, Requirement(False, str(exc), ("N1 frame length above the minimum shift",)))

    task_u = pair_upper(ready.X["TASK"])
    pre_u = pair_upper(ready.X["PRE"])
    post_u = pair_upper(ready.X["POST"])
    r_pre = vector_pearson(task_u, pre_u)
    r_post = vector_pearson(task_u, post_u)
    score = r_post - r_pre

    pre_c, pre_inv, pre_iu = _prepare_shift(ready.X["PRE"])
    post_c, post_inv, post_iu = _prepare_shift(ready.X["POST"])
    null = np.empty(params.n_shuffles, dtype=np.float64)
    for s in range(params.n_shuffles):
        r_post_s = vector_pearson(task_u, _upper_shifted(post_c, post_inv, post_iu, off_post[s]))
        r_pre_s = vector_pearson(task_u, _upper_shifted(pre_c, pre_inv, pre_iu, off_pre[s]))
        null[s] = r_post_s - r_pre_s

    details = _details(rec, ready, r_post, r_pre, null)
    finite = null[np.isfinite(null)]
    if not np.isfinite(score) or finite.size == 0:
        return _fail(
            rec,
            params,
            seed,
            Requirement(
                False,
                "D1 undefined: a pair-correlation vector has zero variance",
                ("pair-correlation vectors with nonzero variance",),
            ),
            details,
        )
    return MethodResult(
        METHOD_ID,
        rec.session_id,
        True,
        "",
        float(score),
        n1_pvalue(float(score), finite),
        params.n_shuffles,
        seed,
        asdict(params),
        details,
    )
