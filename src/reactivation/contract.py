"""Shared data and return contracts (plans/engineer-b.md sections 2.1 and 2.2).

Bootstrap file: frozen after merge; changes only by a PR both engineers approve.
Field names are fixed by research/team-brief.md section 4; dtypes and shapes are
[TEAM DECISION] proposals from the plan.
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
    onset: np.ndarray  # int64, (n_stim,), frame index, inclusive
    offset: np.ndarray  # int64, (n_stim,), frame index, exclusive
    stim_id: np.ndarray  # str, (n_stim,)


@dataclass(frozen=True)
class Recording:
    deconv: np.ndarray  # float64, (n_cells, n_frames); raw deconvolved, never smoothed
    sleep_stage: np.ndarray  # str '<U8', (n_frames,), SleepStage values
    epoch: np.ndarray  # str '<U4', (n_frames,), Epoch values; loader derives it
    fs: float  # frame rate, Hz
    cell_id: np.ndarray  # str, (n_cells,); same cells in PRE, TASK, POST
    mouse_id: str
    session_id: str
    session_type: SessionType
    stim_frames: StimFrames | None  # required "if a task exists"


def analysis_mask(rec: Recording, epoch: Literal["PRE", "TASK", "POST"]) -> np.ndarray:
    """bool (n_frames,). The single definition of which frames a method sees.

    PRE  -> epoch == "PRE"  & sleep_stage == "NREM"   [brief: PRE and POST use NREM frames only]
    POST -> epoch == "POST" & sleep_stage == "NREM"   [brief]
    TASK -> epoch == "TASK" & sleep_stage != "unscored"   [TEAM DECISION, plan Q5]
    """
    if epoch in ("PRE", "POST"):
        return (rec.epoch == epoch) & (rec.sleep_stage == "NREM")
    if epoch == "TASK":
        return (rec.epoch == "TASK") & (rec.sleep_stage != "unscored")
    raise ValueError(f"epoch must be PRE, TASK or POST, got {epoch!r}")


@dataclass(frozen=True)
class Requirement:
    eligible: bool
    reason: str  # "" if eligible; else the first failed requirement, with numbers
    missing: tuple[str, ...]  # data the method would need, e.g. ("POST NREM frames >= 300",)


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return _jsonable(x.tolist())
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return None if math.isnan(x) or math.isinf(x) else x
    if isinstance(x, np.str_):
        return str(x)
    return x


@dataclass(frozen=True)
class MethodResult:
    method_id: str  # "M1".."M4", team-brief IDs
    session_id: str
    eligible: bool
    reason: str
    score: float  # nan if not eligible
    p_n1: float  # nan if not eligible; one-sided p against N1
    n_shuffles: int  # 500 [brief]
    seed: int
    params: dict  # every parameter used, for the results file
    details: dict  # method-specific: n_sig, eigenvalues, bounds, per-component deltas
    missing: tuple[str, ...] = field(default=())

    def to_json(self) -> str:
        """nan -> null, sort_keys=True, so equal results give equal bytes."""
        return json.dumps(_jsonable(asdict(self)), sort_keys=True, allow_nan=False)
