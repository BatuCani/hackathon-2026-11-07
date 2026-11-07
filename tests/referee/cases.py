"""The four referee cases, built on Engineer B's generator (`toolbox.synth.make_session`).

The referee adds one thing the generator lacks: case d, a firing-rate change without a
co-activity change (the Tingley & Peyrache rate confound). It is a perturbation of a
no-sleep-co-activity session: extra independent events on the TASK assembly
members in POST NREM, passed through the same AR(1) calcium filter.

    a_reactivation  co-active in TASK and POST, not in PRE            -> yes
    b_noise         no assemblies anywhere                            -> no
    c_preexisting   co-active in TASK, and equally in PRE and POST    -> no
    d_rate_only     co-active in TASK only; members fire more in POST -> no
"""

from __future__ import annotations

import dataclasses
import zlib

import numpy as np
from toolbox.contract import Recording, analysis_mask
from toolbox.synth import make_session
from scipy.signal import lfilter

CASES: tuple[str, ...] = ("a_reactivation", "b_noise", "c_preexisting", "d_rate_only")
EXPECTED_YES: dict[str, bool] = {
    "a_reactivation": True,
    "b_noise": False,
    "c_preexisting": False,
    "d_rate_only": False,
}
# Assembly activation probability per frame (TASK frames, NREM frames of PRE / POST).
P_TASK, P_SLEEP = 0.03, 0.02
P_ACTIVATION = {
    "a_reactivation": {"PRE": 0.0, "TASK": P_TASK, "POST": P_SLEEP},
    "b_noise": {"PRE": 0.0, "TASK": 0.0, "POST": 0.0},
    "c_preexisting": {"PRE": P_SLEEP, "TASK": P_TASK, "POST": P_SLEEP},
    "d_rate_only": {"PRE": 0.0, "TASK": P_TASK, "POST": 0.0},
}

# Session shape: RIKEN frame rate, PRE / POST NREM frames between Split A and Split B
# (research/datasets/calcium-vetting.md), small enough for the 30 s budget.
N_CELLS = 40
N_ASSEMBLIES, ASSEMBLY_SIZE = 3, 8  # disjoint: cells 0-23
FS = 7.65
FRAMES = {"PRE": 800, "TASK": 600, "POST": 800}
NREM_FRACTION = 0.7  # 560 NREM frames per sleep epoch
# AR(1) a = exp(-1 / (TAU_S * FS)) = 0.30: the 75th percentile of the per-cell lag-1
# autocorrelation of RIKEN `spike`, segment 0 (median 0.17).
TAU_S = 0.11
# Case d: independent extra events on every member in POST NREM, 1 Hz = twice the median
# background rate of `toolbox.synth.make_session` (0.5 Hz); member activity POST / PRE
# comes out at about 2.3 (test_referee_cases.py).
EXTRA_RATE_HZ = 1.0


def members() -> list[np.ndarray]:
    """Assembly member cells (none in case b)."""
    return [np.arange(k * ASSEMBLY_SIZE, (k + 1) * ASSEMBLY_SIZE) for k in range(N_ASSEMBLIES)]


def _add_rate_change(rec: Recording, seed: int) -> Recording:
    """Members get independent extra events in POST NREM; co-activity stays zero."""
    rng = np.random.default_rng([seed, zlib.crc32(b"referee-rate-only")])
    post = analysis_mask(rec, "POST")
    cells = np.concatenate(members())
    p_extra = EXTRA_RATE_HZ / FS
    extra = np.zeros((cells.size, rec.deconv.shape[1]))
    fire = rng.random((cells.size, int(post.sum()))) < p_extra
    extra[:, post] = fire * rng.lognormal(0.0, 0.5, fire.shape)
    a = np.exp(-1.0 / (TAU_S * FS))
    X = rec.deconv.copy()
    X[cells] += lfilter([1.0], [1.0, -a], extra, axis=1)
    return dataclasses.replace(rec, deconv=X)


def make_case(case: str, seed: int) -> Recording:
    """One referee session; same (case, seed) gives identical bytes, cases never share noise."""
    rec = make_session(
        n_cells=N_CELLS, fs=FS, frames=dict(FRAMES), nrem_fraction=NREM_FRACTION,
        assemblies=[] if case == "b_noise" else members(),
        p_activation=dict(P_ACTIVATION[case]), tau_s=TAU_S,
        seed=seed * len(CASES) + CASES.index(case),
        session_id=f"referee-{case}-{seed}",
    )
    return _add_rate_change(rec, seed) if case == "d_rate_only" else rec
