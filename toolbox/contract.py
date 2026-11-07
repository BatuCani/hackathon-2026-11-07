"""Shared contracts: the data contract and the method return type.

Copied from plans/engineer-b.md section 2. Shared by every engineer; change only
with the agreement of A, B and Zixi. Field names follow the loader table in
research/team-brief.md section 4.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from typing import Literal

import numpy as np

SleepStage = Literal["wake", "NREM", "REM", "unscored"]
Epoch = Literal["PRE", "TASK", "POST", "none"]
SessionType = Literal["baseline", "training", "test", "spontaneous"]


@dataclass(frozen=True)
class StimFrames:
    """Onset, offset and identity of each stimulus (required if a task exists)."""

    onset: np.ndarray  # int64, (n_stim,), frame index, inclusive
    offset: np.ndarray  # int64, (n_stim,), frame index, exclusive
    stim_id: np.ndarray  # str, (n_stim,)


@dataclass(frozen=True)
class Recording:
    """One session (or one split of a session) as the loader delivers it."""

    deconv: np.ndarray  # float64, (n_cells, n_frames); raw deconvolved, never smoothed
    sleep_stage: np.ndarray  # str, (n_frames,), SleepStage values
    epoch: np.ndarray  # str, (n_frames,), Epoch values; derived by the loader
    fs: float  # frame rate, Hz
    cell_id: np.ndarray  # str, (n_cells,); same cells in PRE, TASK, POST
    mouse_id: str
    session_id: str
    session_type: SessionType
    stim_frames: StimFrames | None  # required if a task exists


def analysis_mask(rec: Recording, epoch: Literal["PRE", "TASK", "POST"]) -> np.ndarray:
    """Return the bool (n_frames,) mask of frames a method sees for ``epoch``.

    The single definition shared by all methods:
    PRE  -> epoch == "PRE"  and sleep_stage == "NREM";
    POST -> epoch == "POST" and sleep_stage == "NREM";
    TASK -> epoch == "TASK" and sleep_stage != "unscored" (team decision, open
    question Q5 in plans/engineer-b.md).
    """
    raise NotImplementedError("analysis_mask: implement with the loader (task T1)")


@dataclass(frozen=True)
class Requirement:
    """Outcome of a method's requirement check."""

    eligible: bool
    reason: str  # "" if eligible; else the first failed requirement, with numbers
    missing: tuple[str, ...]  # data the method would need, e.g. ("POST NREM frames >= 300",)


def _nan_to_none(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {k: _nan_to_none(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_nan_to_none(v) for v in value]
    if isinstance(value, np.ndarray):
        return _nan_to_none(value.tolist())
    if isinstance(value, np.generic):
        return _nan_to_none(value.item())
    return value


@dataclass(frozen=True)
class MethodResult:
    """What every method M1-M4 returns for one session or split."""

    method_id: str  # "M1".."M4", team-brief IDs
    session_id: str
    eligible: bool
    reason: str
    score: float  # nan if not eligible
    p_n1: float  # nan if not eligible; one-sided p against N1
    n_shuffles: int  # 500
    seed: int
    params: dict  # every parameter used, for the results file
    details: dict  # method-specific: n_sig, eigenvalues, bounds, per-component deltas
    missing: tuple[str, ...] = field(default=())

    def to_json(self) -> str:
        """Serialize deterministically: nan -> null, sorted keys, equal results give equal bytes."""
        return json.dumps(_nan_to_none(asdict(self)), sort_keys=True, allow_nan=False)
