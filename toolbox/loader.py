"""Loader for the RIKEN Zenodo 17667863 ``sleep_data.mat`` (owner: Engineer A, task T1).

Builds one :class:`toolbox.contract.Recording` per split (A and B, see PROBLEM.md):
``deconv`` from ``spike``, ``sleep_stage`` from ``state.state``, ``fs = 7.65`` Hz,
``epoch`` (PRE / TASK / POST) from the split definitions. A missing required field
stops with a clear message. Never commits or copies the data into the repository.

Variable names and their meaning follow the dataset authors' own MATLAB loader
(``load_data_demo.m`` and ``load_sleep_or_ane_data.m`` in
https://github.com/oizumi-lab/mouse_network_2P, used as reference only: that
repository has no licence, so no code is copied). Quoted from ``load_data_demo.m``:
"spike: NxT deconvolved spike matrix", "SleepState: 0: Awake, 0.5: Quiet wake,
1: NREM, 2: REM", "boundary_ind: ... frames are not recorded continuously".
Their loader reads the file with ``load(..., 'smoothed_spike', 'ROIs', 'frame', 'state')``;
we read ``spike`` instead (raw deconvolution, never smoothed; team brief section 4).

Split frame ranges are the 0-based half-open TASK windows from
research/datasets/calcium-vetting.md ("Recommended splits"). Each split is cut to
its own recording segment, so nothing downstream can cross ``boundary_ind``.

Cell selection (decided by the team lead, PROBLEM.md "Not decided yet"): the
``n_cells`` cells (default 300) with the highest mean ``spike`` over the union of
both splits' TASK frames (the full wake bouts), selected once, so splits A and B
use the same cells (needed for M2). No cap: Split B (651 TASK frames) then fails
M3/M4's "TASK frames >= 5 x cells" and the methods report it as not eligible.
Still awaiting the scientist's signature. ``n_cells=None`` keeps all 6,920 cells.

Cache: the first load of a ``.mat`` writes a compressed ``.npz`` (``spike`` as
float32 plus the small fields) to ``/Users/batu/hackathon-data/riken/cache/``
(override with ``RIKEN_CACHE_DIR``), outside the repository; later loads read it.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .contract import Recording

FS_HZ = 7.65  # data description paper (bioRxiv doi:10.64898/2026.07.20.739676); not in the file
MOUSE_ID = "mouse05"  # durations match mouse05 in Table 2 of the data description (vetting report)
SESSION_TYPE = "spontaneous"
DEFAULT_DATA = Path(os.environ.get("RIKEN_SLEEP_DATA", "/Users/batu/hackathon-data/riken/mouse_data/sleep_data.mat"))
DEFAULT_CACHE_DIR = Path(os.environ.get("RIKEN_CACHE_DIR", "/Users/batu/hackathon-data/riken/cache"))
DEFAULT_N_CELLS = 300  # team-lead decision, PROBLEM.md; awaiting the scientist's signature

# state.state code -> SleepStage; anything else (5 interpolation artefacts at bout edges) -> unscored.
STAGE_CODES = {0.0: "wake", 0.5: "wake", 1.0: "NREM", 2.0: "REM"}


@dataclass(frozen=True)
class Split:
    """One split: a recording segment and its TASK wake bout, 0-based half-open frame indices."""

    split_id: str
    segment: int  # index into the segments defined by frame.boundary_ind
    task_start: int  # first TASK frame, absolute
    task_stop: int  # one past the last TASK frame, absolute


# calcium-vetting.md "Recommended splits": A TASK = frames 5481-7306, B TASK = frames 15006-15657.
SPLITS = {
    "A": Split("A", segment=0, task_start=5481, task_stop=7306),
    "B": Split("B", segment=1, task_start=15006, task_stop=15657),
}


class LoaderError(ValueError):
    """The data file lacks a required field or is inconsistent with the split definitions."""


@dataclass(frozen=True)
class RawSession:
    """The fields read from ``sleep_data.mat``, before splitting."""

    spike: np.ndarray  # float32, (n_cells, n_frames)
    state: np.ndarray  # float64, (n_frames,), state.state codes
    boundary_ind: np.ndarray  # int64, segment ends (MATLAB 1-based last frame == 0-based stop)
    atlas_id: np.ndarray  # int64, (n_cells,), ROIs.atlasID


# ---- reading ----------------------------------------------------------------------------------


def _require(obj, name: str, path: Path):
    if obj is None:
        raise LoaderError(f"{path}: required field {name!r} is missing; cannot build the data contract")
    return obj


def _read_mat_v5(path: Path) -> dict:
    import scipy.io as sio

    # Never call loadmat without variable_names: the opaque MATLAB object `st` breaks scipy,
    # and `dFF` (1 GB) must never be loaded (vetting report).
    try:
        m = sio.loadmat(path, variable_names=["spike", "state", "frame", "ROIs"], squeeze_me=True, struct_as_record=False)
    except Exception as e:  # noqa: BLE001
        raise LoaderError(f"{path}: cannot read as MATLAB v5 file: {e}") from e

    def field(var: str, sub: str | None):
        v = m.get(var)
        if v is None or sub is None:
            return v
        return getattr(v, sub, None)

    return {
        "spike": field("spike", None),
        "state.state": field("state", "state"),
        "frame.boundary_ind": field("frame", "boundary_ind"),
        "ROIs.atlasID": field("ROIs", "atlasID"),
    }


def _read_mat_v73(path: Path) -> dict:
    import h5py

    out = {}
    with h5py.File(path, "r") as f:
        for key in ("spike", "state/state", "frame/boundary_ind", "ROIs/atlasID"):
            name = key.replace("/", ".")
            if key not in f:
                out[name] = None
                continue
            a = f[key]
            # MATLAB stores column-major: an N x T matrix appears as T x N in HDF5.
            out[name] = (a[()].astype(np.float32).T if key == "spike" else np.asarray(a[()]).ravel())
    return out


def read_mat(path: Path) -> RawSession:
    """Read the required fields from ``sleep_data.mat`` (MATLAB v5 or v7.3)."""
    path = Path(path)
    if not path.exists():
        raise LoaderError(f"{path}: file not found (RIKEN Zenodo 17667863, mouse_data/sleep_data.mat)")
    import h5py

    fields = _read_mat_v73(path) if h5py.is_hdf5(path) else _read_mat_v5(path)
    spike = np.asarray(_require(fields["spike"], "spike", path), dtype=np.float32)
    state = np.asarray(_require(fields["state.state"], "state.state", path), dtype=np.float64).ravel()
    boundary = np.asarray(_require(fields["frame.boundary_ind"], "frame.boundary_ind", path)).astype(np.int64).ravel()
    atlas = np.asarray(_require(fields["ROIs.atlasID"], "ROIs.atlasID", path)).astype(np.int64).ravel()
    return _validate(RawSession(spike=spike, state=state, boundary_ind=boundary, atlas_id=atlas), path)


def _validate(raw: RawSession, path: Path) -> RawSession:
    if raw.spike.ndim != 2:
        raise LoaderError(f"{path}: 'spike' must be cells x frames, got shape {raw.spike.shape}")
    n_cells, n_frames = raw.spike.shape
    if raw.state.shape != (n_frames,):
        raise LoaderError(f"{path}: 'state.state' has {raw.state.size} frames, 'spike' has {n_frames}")
    if raw.atlas_id.shape != (n_cells,):
        raise LoaderError(f"{path}: 'ROIs.atlasID' has {raw.atlas_id.size} cells, 'spike' has {n_cells}")
    if raw.boundary_ind.size == 0 or raw.boundary_ind[-1] != n_frames or np.any(np.diff(raw.boundary_ind) <= 0):
        raise LoaderError(f"{path}: 'frame.boundary_ind' {raw.boundary_ind.tolist()} does not end at {n_frames} frames")
    if not np.all(np.isfinite(raw.spike)):
        raise LoaderError(f"{path}: 'spike' contains NaN or inf")
    return raw


# ---- cache ------------------------------------------------------------------------------------


def _cache_path(mat_path: Path, cache_dir: Path) -> Path:
    st = mat_path.stat()
    key = hashlib.sha1(f"{mat_path.resolve()}|{st.st_size}|{int(st.st_mtime)}".encode()).hexdigest()[:12]
    return cache_dir / f"{mat_path.stem}_{key}.npz"


def save_npz(raw: RawSession, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, spike=raw.spike, state=raw.state, boundary_ind=raw.boundary_ind, atlas_id=raw.atlas_id)
    tmp.replace(path)
    return path


def read_npz(path: Path) -> RawSession:
    path = Path(path)
    with np.load(path) as z:
        missing = [k for k in ("spike", "state", "boundary_ind", "atlas_id") if k not in z.files]
        if missing:
            raise LoaderError(f"{path}: cached file lacks {missing}; delete it to rebuild from the .mat")
        raw = RawSession(spike=z["spike"].astype(np.float32, copy=False), state=z["state"],
                         boundary_ind=z["boundary_ind"], atlas_id=z["atlas_id"])
    return _validate(raw, path)


def load_raw(path: Path | str | None = None, *, cache_dir: Path | str | None = DEFAULT_CACHE_DIR) -> RawSession:
    """Read ``sleep_data.mat`` or a cached ``.npz``; with ``cache_dir``, read or write the cache."""
    path = Path(path) if path is not None else DEFAULT_DATA
    if path.suffix == ".npz":
        return read_npz(path)
    if cache_dir is None:
        return read_mat(path)
    if not path.exists():
        raise LoaderError(f"{path}: file not found (RIKEN Zenodo 17667863, mouse_data/sleep_data.mat)")
    cached = _cache_path(path, Path(cache_dir))
    if cached.exists():
        return read_npz(cached)
    raw = read_mat(path)
    save_npz(raw, cached)
    return raw


# ---- contract ---------------------------------------------------------------------------------


def sleep_stages(state: np.ndarray) -> np.ndarray:
    """Map ``state.state`` codes to SleepStage strings (PROBLEM.md "Data and fixed choices")."""
    out = np.full(state.shape, "unscored", dtype="<U8")
    for code, stage in STAGE_CODES.items():
        out[state == code] = stage
    return out


def task_frames(split_ids: tuple[str, ...]) -> np.ndarray:
    """Absolute frame indices of the union of the splits' TASK windows (full wake bouts)."""
    for s in split_ids:
        if s not in SPLITS:
            raise LoaderError(f"unknown split {s!r}; known: {sorted(SPLITS)}")
    return np.concatenate([np.arange(SPLITS[s].task_start, SPLITS[s].task_stop) for s in split_ids])


def select_cells(task_deconv: np.ndarray, n_cells: int | None) -> np.ndarray:
    """Sorted indices of the ``n_cells`` most active cells by mean TASK activity, ties by lower index."""
    n_total = task_deconv.shape[0]
    if n_cells is None or n_cells >= n_total:
        return np.arange(n_total)
    if n_cells < 1:
        raise LoaderError(f"cell selection: n_cells must be >= 1 or None, got {n_cells}")
    order = np.lexsort((np.arange(n_total), -task_deconv.mean(axis=1, dtype=np.float64)))
    return np.sort(order[:n_cells])


def build_split(raw: RawSession, split_id: str, cells: np.ndarray | None = None) -> Recording:
    """One split as a Recording, cut to its own recording segment (frame indices relative to it).

    ``cells`` are row indices into ``spike`` (default: all cells); pass the same array for every
    split so that PRE, TASK and POST of both splits hold the same cells.
    """
    if split_id not in SPLITS:
        raise LoaderError(f"unknown split {split_id!r}; known: {sorted(SPLITS)}")
    sp = SPLITS[split_id]
    edges = np.concatenate([[0], raw.boundary_ind])
    if sp.segment >= raw.boundary_ind.size:
        raise LoaderError(f"split {split_id}: segment {sp.segment} absent, frame.boundary_ind = {raw.boundary_ind.tolist()}")
    seg_start, seg_stop = int(edges[sp.segment]), int(edges[sp.segment + 1])
    if not seg_start < sp.task_start < sp.task_stop < seg_stop:
        raise LoaderError(f"split {split_id}: TASK {sp.task_start}-{sp.task_stop} not inside segment {seg_start}-{seg_stop}")

    stage = sleep_stages(raw.state[seg_start:seg_stop])
    t0, t1 = sp.task_start - seg_start, sp.task_stop - seg_start
    if np.any(stage[t0:t1] == "NREM") or np.any(stage[t0:t1] == "REM"):
        raise LoaderError(f"split {split_id}: TASK {sp.task_start}-{sp.task_stop} is not a wake bout in this file")
    epoch = np.full(seg_stop - seg_start, "POST", dtype="<U4")
    epoch[:t0] = "PRE"
    epoch[t0:t1] = "TASK"

    cells = np.arange(raw.spike.shape[0]) if cells is None else np.asarray(cells)
    seg = raw.spike[:, seg_start:seg_stop]
    return Recording(
        deconv=np.ascontiguousarray(seg[cells], dtype=np.float64),
        sleep_stage=stage,
        epoch=epoch,
        fs=FS_HZ,
        cell_id=np.array([str(c) for c in cells]),
        mouse_id=MOUSE_ID,
        session_id=f"{MOUSE_ID}_split{split_id}",
        session_type=SESSION_TYPE,
        stim_frames=None,  # no task in this dataset; the wake bout stands in for TASK
    )


def load_sessions(
    path: Path | str | None = None,
    *,
    n_cells: int | None = DEFAULT_N_CELLS,
    cache_dir: Path | str | None = DEFAULT_CACHE_DIR,
    splits: tuple[str, ...] = ("A", "B"),
) -> list[Recording]:
    """Split A and Split B of ``sleep_data.mat`` (or its cached ``.npz``) as Recordings.

    The same ``n_cells`` most active cells, selected over the union of the splits' TASK frames.
    """
    raw = load_raw(path, cache_dir=cache_dir)
    cells = select_cells(raw.spike[:, task_frames(splits)], n_cells)
    return [build_split(raw, s, cells) for s in splits]


def describe(recs: list[Recording]) -> dict:
    """Frame and cell counts per split, the numbers the vetting report and tests check."""
    from .contract import analysis_mask

    return {
        r.session_id: {
            "n_cells": int(r.deconv.shape[0]),
            "n_frames": int(r.deconv.shape[1]),
            "fs": r.fs,
            "PRE_NREM": int(analysis_mask(r, "PRE").sum()),
            "TASK_frames": int((r.epoch == "TASK").sum()),
            "TASK_scored": int(analysis_mask(r, "TASK").sum()),
            "POST_NREM": int(analysis_mask(r, "POST").sum()),
        }
        for r in recs
    }


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser(description="Print per-split frame and cell counts as JSON (builds the cache).")
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--n-cells", type=int, default=DEFAULT_N_CELLS, help="0 = all cells")
    a = ap.parse_args()
    print(json.dumps(describe(load_sessions(a.data, n_cells=a.n_cells or None)), indent=1, sort_keys=True))
