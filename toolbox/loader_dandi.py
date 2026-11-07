"""Loader for DANDI:000044 (Grosmark & Buzsaki 2016, rat CA1 silicon probes, CC-BY-4.0).

https://dandiarchive.org/dandiset/000044/0.261106.0236 ; vetted in research/datasets/ephys.md.
Builds one :class:`toolbox.contract.Recording` per session:

- ``deconv``: spike counts per bin (units x bins). Not deconvolved calcium: the field name is
  fixed by the contract; for ephys the binned counts take its place (SoT "Shared preprocessing").
- ``epoch``: from ``intervals/epochs`` (PRE -> PRE, MAZE -> TASK, POST -> POST), by bin centre.
- ``sleep_stage``: from ``processing/behavior/sleep_states_buzcode`` (WAKE/NREM/REM), by bin centre;
  bins outside every labelled interval are ``unscored``.
- ``cell_id``: the NWB unit id; default keeps ``cell_type == "pyramidal cell"`` only.

Defaults are [TEAM DECISION]s: bin 100 ms (SoT A41: reactivation bins about 50-200 ms),
pyramidal cells only. ``source`` is a local path or an https URL; URLs stream with ``remfile``
(not a project dependency: ``uv run --with remfile ...``).
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import h5py
import numpy as np

from .contract import Recording

DANDISET, VERSION = "000044", "0.261106.0236"
EPOCH_MAP = {"PRE": "PRE", "MAZE": "TASK", "POST": "POST"}
STATE_MAP = {"WAKE": "wake", "NREM": "NREM", "REM": "REM"}
REQUIRED = ("intervals/epochs", "units/spike_times", "units/spike_times_index", "processing/behavior/sleep_states_buzcode")


def dandi_urls() -> dict[str, str]:
    """{session path: download URL} for the 8 sessions, from the DANDI REST API."""
    api = f"https://api.dandiarchive.org/api/dandisets/{DANDISET}/versions/{VERSION}/assets/?page_size=100"
    with urllib.request.urlopen(api, timeout=30) as r:
        assets = json.load(r)["results"]
    return {a["path"]: f"https://api.dandiarchive.org/api/assets/{a['asset_id']}/download/" for a in assets}


def _open(source) -> h5py.File:
    s = str(source)
    if s.startswith(("http://", "https://")):
        try:
            import remfile
        except ImportError as e:
            raise ImportError("streaming a URL needs remfile: uv run --with remfile ...") from e
        return h5py.File(remfile.File(s), "r")
    return h5py.File(s, "r")


def _str(values) -> np.ndarray:
    return np.array([v.decode() if isinstance(v, bytes) else str(v) for v in values])


def _label_bins(centres: np.ndarray, start, stop, labels, mapping: dict, default: str, dtype: str) -> np.ndarray:
    out = np.full(centres.size, default, dtype=dtype)
    for a, b, lab in zip(start, stop, labels):
        if lab in mapping:
            out[(centres >= a) & (centres < b)] = mapping[lab]
    return out


def load_dandi44(
    source,
    *,
    bin_s: float = 0.1,
    cell_types: tuple[str, ...] | None = ("pyramidal cell",),
    task_unscored_as_wake: bool = False,
    session_id: str | None = None,
) -> Recording:
    """Load one DANDI:000044 NWB session into a Recording. Missing required field -> ValueError."""
    with _open(source) as f:
        for key in REQUIRED:
            if key not in f:
                raise ValueError(f"DANDI:000044 loader: required field '{key}' missing in {source}")
        ep = f["intervals/epochs"]
        ep_start, ep_stop, ep_lab = ep["start_time"][:], ep["stop_time"][:], _str(ep["label"][:])
        st = f["processing/behavior/sleep_states_buzcode"]
        st_start, st_stop, st_lab = st["start_time"][:], st["stop_time"][:], _str(st["label"][:])
        u = f["units"]
        times, index = u["spike_times"][:], u["spike_times_index"][:]
        ids = _str(u["id"][:])
        ctype = _str(u["cell_type"][:]) if "cell_type" in u else np.full(ids.size, "unknown")
        sid = session_id or (f["general/session_id"][()] if "general/session_id" in f else Path(str(source)).stem)
        subject = f["general/subject/subject_id"][()] if "general/subject/subject_id" in f else "unknown"

    missing = sorted(set(EPOCH_MAP) - set(ep_lab))
    if missing:
        raise ValueError(f"DANDI:000044 loader: epochs {missing} missing in intervals/epochs label")

    n_bins = int(np.floor(ep_stop.max() / bin_s + 1e-9))
    edges = np.arange(n_bins + 1) * bin_s
    centres = edges[:-1] + bin_s / 2
    keep = np.arange(ids.size) if cell_types is None else np.flatnonzero(np.isin(ctype, cell_types))
    bounds = np.concatenate([[0], index])
    counts = np.vstack([np.histogram(times[bounds[i] : bounds[i + 1]], bins=edges)[0] for i in keep]).astype(np.float64)

    epoch = _label_bins(centres, ep_start, ep_stop, ep_lab, EPOCH_MAP, "none", "<U4")
    stage = _label_bins(centres, st_start, st_stop, st_lab, STATE_MAP, "unscored", "<U8")
    if task_unscored_as_wake:
        stage[(epoch == "TASK") & (stage == "unscored")] = "wake"

    as_str = lambda x: x.decode() if isinstance(x, bytes) else str(x)  # noqa: E731
    return Recording(
        deconv=counts,
        sleep_stage=stage,
        epoch=epoch,
        fs=1.0 / bin_s,
        cell_id=ids[keep],
        mouse_id=as_str(subject),
        session_id=as_str(sid),
        session_type="training",  # novel maze per session_description
        stim_frames=None,  # no stimuli; M1-M4 do not need them
    )
