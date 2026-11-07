"""M2 explained variance vs. reverse, EV / REV (owner: Engineer A).

Key D2 = EV - REV (PROBLEM.md), per split; the verdict runs across splits A and B as pseudo-sessions.

EV = ((r_T,POST - r_T,PRE r_PRE,POST) / sqrt((1 - r_T,PRE^2)(1 - r_PRE,POST^2)))^2
(research/team-brief.md section 4, research/source-of-truth.md M2), REV = the same with PRE and POST swapped.
r(A, B) is the Pearson correlation between the flattened upper triangles (k=1) of the cell-pair
correlation matrices of epochs A and B.

p_n1: N1 per-neuron circular shift of PRE and POST NREM frames (toolbox/nulls.py), TASK fixed.
details.p_blockswap (supplementary, as M3): PRE and POST NREM frames cut into ``blockswap_s`` blocks,
block labels permuted between PRE and POST; catches TASK patterns already present in PRE, which N1
alone flags as "yes" (tests/test_m2.py, pre_existing control).

Exposes ``check_requirements(rec, params)``, ``run(rec, *, seed, params=None)`` returning
:class:`toolbox.contract.MethodResult`, and ``verdict(results)`` for the cross-split rule.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .contract import MethodResult, Recording, Requirement, analysis_mask
from .nulls import n1_offsets, n1_pvalue, rng_for, circular_shift

METHOD_ID = "M2"
CAVEAT = (
    "M2 needs at least two sessions; only two pseudo-sessions exist "
    "(splits A and B of one recording, same animal, mouse05), so a 'yes' is not independent replication."
)


@dataclass(frozen=True)
class M2Params:
    n_shuffles: int = 500
    min_nrem_frames: int = 300  # PRE and POST, PROBLEM.md eligibility "as M1"
    min_cells: int = 4  # 3 cells give 3 pairs: partial correlation of 3 points is always +-1
    min_task_frames: int = 2
    alpha: float = 0.05
    blockswap_s: float = 20.0  # supplementary null: PRE/POST NREM frames cut into blocks, labels permuted


def pair_corr_vec(X: np.ndarray) -> np.ndarray:
    """Upper triangle (k=1) of the cell-pair Pearson correlation matrix of X (cells x frames).

    Pairs with a constant cell come out nan and are dropped later by ``coherences``.
    """
    Xc = X - X.mean(axis=1, keepdims=True)
    sd = np.sqrt(np.sum(Xc * Xc, axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        Z = Xc / sd[:, None]
    C = Z @ Z.T
    iu = np.triu_indices(X.shape[0], k=1)
    return C[iu]


def _r(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    den = np.sqrt(np.dot(a, a) * np.dot(b, b))
    return float(np.dot(a, b) / den) if den > 0 else float("nan")


def coherences(c_task: np.ndarray, c_pre: np.ndarray, c_post: np.ndarray) -> tuple[float, float, float]:
    """(r_T,POST, r_T,PRE, r_PRE,POST) over pairs finite in all three epochs."""
    ok = np.isfinite(c_task) & np.isfinite(c_pre) & np.isfinite(c_post)
    t, pre, post = c_task[ok], c_pre[ok], c_post[ok]
    return _r(t, post), _r(t, pre), _r(pre, post)


def ev(r_t_post: float, r_t_pre: float, r_pre_post: float) -> float:
    """Squared partial correlation of TASK-POST given PRE (team brief section 4)."""
    den = np.sqrt((1.0 - r_t_pre**2) * (1.0 - r_pre_post**2))
    if not den > 0:
        return float("nan")
    return float(((r_t_post - r_t_pre * r_pre_post) / den) ** 2)


def ev_rev(r_t_post: float, r_t_pre: float, r_pre_post: float) -> tuple[float, float]:
    """(EV, REV); REV swaps PRE and POST: r_T,POST <-> r_T,PRE, r_PRE,POST unchanged (symmetric)."""
    return ev(r_t_post, r_t_pre, r_pre_post), ev(r_t_pre, r_t_post, r_pre_post)


def d2_from_vectors(c_task: np.ndarray, c_pre: np.ndarray, c_post: np.ndarray) -> dict:
    r_tpost, r_tpre, r_prepost = coherences(c_task, c_pre, c_post)
    e, rev = ev_rev(r_tpost, r_tpre, r_prepost)
    return {"r_task_post": r_tpost, "r_task_pre": r_tpre, "r_pre_post": r_prepost,
            "ev": e, "rev": rev, "d2": e - rev}


def _epochs(rec: Recording) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = rec.deconv
    return (X[:, analysis_mask(rec, "TASK")], X[:, analysis_mask(rec, "PRE")], X[:, analysis_mask(rec, "POST")])


def check_requirements(rec: Recording, params: M2Params | None = None) -> Requirement:
    p = params or M2Params()
    n_cells = rec.deconv.shape[0]
    n_task = int(analysis_mask(rec, "TASK").sum())
    n_pre = int(analysis_mask(rec, "PRE").sum())
    n_post = int(analysis_mask(rec, "POST").sum())
    if n_cells < p.min_cells:
        return Requirement(False, f"{n_cells} cells < {p.min_cells}", (f"cells >= {p.min_cells}",))
    if n_task < p.min_task_frames:
        return Requirement(False, f"{n_task} TASK frames < {p.min_task_frames}", (f"TASK frames >= {p.min_task_frames}",))
    if n_pre < p.min_nrem_frames:
        return Requirement(False, f"{n_pre} PRE NREM frames < {p.min_nrem_frames}", (f"PRE NREM frames >= {p.min_nrem_frames}",))
    if n_post < p.min_nrem_frames:
        return Requirement(False, f"{n_post} POST NREM frames < {p.min_nrem_frames}", (f"POST NREM frames >= {p.min_nrem_frames}",))
    return Requirement(True, "", ())


def run(rec: Recording, *, seed: int, params: M2Params | None = None) -> MethodResult:
    p = params or M2Params()
    par = asdict(p)
    req = check_requirements(rec, p)
    nan = float("nan")
    if not req.eligible:
        return MethodResult(METHOD_ID, rec.session_id, False, req.reason, nan, nan, p.n_shuffles, seed,
                            par, {"caveat": CAVEAT}, req.missing)
    X_task, X_pre, X_post = _epochs(rec)
    c_task = pair_corr_vec(X_task)
    obs = d2_from_vectors(c_task, pair_corr_vec(X_pre), pair_corr_vec(X_post))

    # N1 on PRE and POST separately (each its own analysed frames), TASK template fixed.
    off_pre = n1_offsets(X_pre.shape[0], X_pre.shape[1], p.n_shuffles, rng_for(seed, rec.session_id, "M2/N1/PRE"))
    off_post = n1_offsets(X_post.shape[0], X_post.shape[1], p.n_shuffles, rng_for(seed, rec.session_id, "M2/N1/POST"))
    null = np.empty(p.n_shuffles)
    for i in range(p.n_shuffles):
        null[i] = d2_from_vectors(c_task, pair_corr_vec(circular_shift(X_pre, off_pre[i])),
                                  pair_corr_vec(circular_shift(X_post, off_post[i])))["d2"]
    L = max(1, int(round(p.blockswap_s * rec.fs)))
    blocks = [X_pre[:, i:i + L] for i in range(0, X_pre.shape[1], L)]
    n_pre_blocks = len(blocks)
    blocks += [X_post[:, i:i + L] for i in range(0, X_post.shape[1], L)]
    rng_bs = rng_for(seed, rec.session_id, "M2/blockswap")
    null_bs = np.empty(p.n_shuffles)
    for i in range(p.n_shuffles):
        perm = rng_bs.permutation(len(blocks))
        pre = np.concatenate([blocks[j] for j in perm[:n_pre_blocks]], axis=1)
        post = np.concatenate([blocks[j] for j in perm[n_pre_blocks:]], axis=1)
        null_bs[i] = d2_from_vectors(c_task, pair_corr_vec(pre), pair_corr_vec(post))["d2"]
    details = {
        **obs,
        "p_blockswap": n1_pvalue(obs["d2"], null_bs),
        "blockswap_frames": L,
        "n_cells": int(X_task.shape[0]),
        "n_pairs": int(c_task.size),
        "frames": {"TASK": int(X_task.shape[1]), "PRE": int(X_pre.shape[1]), "POST": int(X_post.shape[1])},
        "null_mean": float(np.nanmean(null)),
        "null_q95": float(np.nanquantile(null, 0.95)),
        "caveat": CAVEAT,
    }
    return MethodResult(METHOD_ID, rec.session_id, True, "", obs["d2"], n1_pvalue(obs["d2"], null),
                        p.n_shuffles, seed, par, details)


def is_yes(r: MethodResult, alpha: float = 0.05, require_blockswap: bool = False) -> bool:
    """Locked key rule: D2 > 0 and p_N1 < alpha; ``require_blockswap`` adds p_blockswap < alpha."""
    yes = bool(r.eligible and r.score > 0 and r.p_n1 < alpha)
    if require_blockswap:
        yes = yes and r.details.get("p_blockswap", 1.0) < alpha
    return yes


def verdict(results: list[MethodResult], alpha: float = 0.05) -> dict:
    """PROBLEM.md key D2: "yes" iff D2 > 0 and p_N1 < alpha in every split (both A and B), with the caveat."""
    per_split = {r.session_id: {"eligible": r.eligible, "d2": r.score, "p_n1": r.p_n1,
                                "p_blockswap": r.details.get("p_blockswap"), "yes": is_yes(r, alpha),
                                "yes_with_blockswap": is_yes(r, alpha, require_blockswap=True)}
                 for r in results}
    if len(results) < 2:
        answer = "not eligible"
        reason = f"{len(results)} session(s); M2 needs at least two"
    elif not all(r.eligible for r in results):
        answer = "not eligible"
        reason = "; ".join(f"{r.session_id}: {r.reason}" for r in results if not r.eligible)
    else:
        answer = "yes" if all(is_yes(r, alpha) for r in results) else "no"
        reason = ""
    both = all(r.eligible for r in results) and len(results) >= 2
    answer_bs = ("yes" if all(is_yes(r, alpha, True) for r in results) else "no") if both else answer
    return {"method_id": METHOD_ID, "answer": answer, "answer_with_blockswap": answer_bs,
            "reason": reason, "alpha": alpha,
            "per_split": per_split, "caveat": CAVEAT}
