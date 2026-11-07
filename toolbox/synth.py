"""Synthetic calcium-like Recording (plans/engineer-b.md Step 1).

Used for method tests (positive / negative controls) only; real `deconv` is never smoothed.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy.signal import lfilter

from .contract import Recording, StimFrames

EPOCHS = ("PRE", "TASK", "POST")


def _split(total: int, parts: int, rng: np.random.Generator) -> np.ndarray:
    """Split `total` frames into `parts` non-negative integer bouts that sum exactly to `total`."""
    if parts == 1:
        return np.array([total])
    cuts = np.sort(rng.integers(0, total + 1, parts - 1))
    return np.diff(np.concatenate([[0], cuts, [total]]))


def _sleep_stages(n: int, nrem_fraction: float, rng: np.random.Generator, n_cycles: int = 10) -> np.ndarray:
    """Alternating NREM / REM / wake bouts with an exact NREM fraction (rounded to a frame)."""
    stages = np.empty(n, dtype="<U8")
    if n == 0:
        return stages
    n_nrem = int(round(nrem_fraction * n))
    n_rest = n - n_nrem
    n_rem = n_rest // 2
    n_wake = n_rest - n_rem
    cycles = max(1, min(n_cycles, n // 30))
    seq = []
    for nrem, rem, wake in zip(_split(n_nrem, cycles, rng), _split(n_rem, cycles, rng), _split(n_wake, cycles, rng)):
        seq += ["NREM"] * nrem + ["REM"] * rem + ["wake"] * wake
    stages[:] = seq
    return stages


def make_session(
    *,
    n_cells: int = 50,
    fs: float = 10.0,
    frames: dict | None = None,
    nrem_fraction: float = 0.7,
    assemblies: Sequence[np.ndarray] = (),
    sleep_assemblies: Sequence[np.ndarray] | None = None,
    p_activation: dict | None = None,
    p_member: float = 0.8,
    tau_s: float = 0.0,
    seed: int = 0,
    session_id: str = "synth",
) -> Recording:
    """Synthetic session: PRE, TASK, POST in that order.

    - Background: per-cell rate lognormal (SoT A40), events Bernoulli(rate / fs) per frame,
      amplitudes lognormal(0, 0.5).
    - Assemblies: per frame and assembly, activation Bernoulli(p_activation[epoch]); when active,
      each member fires with probability p_member. Active only on TASK frames and NREM frames of PRE/POST.
    - `sleep_assemblies` (not in the plan signature): assemblies used in PRE/POST instead of
      `assemblies`, for the "other assemblies" negative control (T-M3-4). Default: same as TASK.
    - tau_s > 0: AR(1) filter, a = exp(-1 / (tau_s * fs)), per cell (calcium-like autocorrelation).
    """
    frames = {"PRE": 5700, "TASK": 6000, "POST": 5700} if frames is None else frames
    p_activation = {"PRE": 0.0, "TASK": 0.02, "POST": 0.005} if p_activation is None else p_activation
    sleep_assemblies = assemblies if sleep_assemblies is None else sleep_assemblies
    rng = np.random.default_rng(seed)

    epoch = np.concatenate([np.full(frames[e], e, dtype="<U4") for e in EPOCHS])
    stage = np.concatenate(
        [
            _sleep_stages(frames["PRE"], nrem_fraction, rng),
            np.full(frames["TASK"], "wake", dtype="<U8"),
            _sleep_stages(frames["POST"], nrem_fraction, rng),
        ]
    )
    n_frames = epoch.size

    rate_hz = np.exp(rng.normal(np.log(0.5), 1.0, n_cells))
    p_event = np.minimum(rate_hz / fs, 0.5)[:, None]
    events = rng.random((n_cells, n_frames)) < p_event
    X = events * rng.lognormal(0.0, 0.5, (n_cells, n_frames))

    for ep in EPOCHS:
        sel = epoch == ep
        if ep != "TASK":
            sel &= stage == "NREM"
        idx = np.flatnonzero(sel)
        for members in assemblies if ep == "TASK" else sleep_assemblies:
            members = np.asarray(members)
            active = idx[rng.random(idx.size) < p_activation[ep]]
            fire = rng.random((members.size, active.size)) < p_member
            amp = rng.lognormal(0.0, 0.5, fire.shape)
            X[np.ix_(members, active)] += fire * amp

    if tau_s > 0:
        a = np.exp(-1.0 / (tau_s * fs))
        X = lfilter([1.0], [1.0, -a], X, axis=1)

    pre_end = frames["PRE"]
    stim = StimFrames(
        onset=np.array([pre_end], dtype=np.int64),
        offset=np.array([pre_end + frames["TASK"]], dtype=np.int64),
        stim_id=np.array(["task"]),
    )
    return Recording(
        deconv=np.ascontiguousarray(X, dtype=np.float64),
        sleep_stage=stage,
        epoch=epoch,
        fs=float(fs),
        cell_id=np.array([f"c{i:03d}" for i in range(n_cells)]),
        mouse_id="synth",
        session_id=session_id,
        session_type="training",
        stim_frames=stim,
    )
