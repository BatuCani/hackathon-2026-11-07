"""T1 loader tests: frame counts per epoch equal the vetting report; missing fields stop clearly.

Real-data tests run when ``sleep_data.mat`` (or ``RIKEN_SLEEP_DATA``) exists and skip otherwise.
Expected counts: research/datasets/calcium-vetting.md "Recommended splits" and PROBLEM.md.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.io as sio

from toolbox import loader
from toolbox.contract import analysis_mask

# Split -> (PRE NREM, TASK frames in the wake bout, TASK frames with a scored stage, POST NREM).
# Split A TASK holds one unscored interpolation frame (7305, state 0.0319): 1825 frames, 1824 scored.
# Split B TASK is 651 frames (85 s); the vetting text rounds it to "650 frames".
EXPECTED = {"A": (1300, 1825, 1824, 999), "B": (2657, 651, 651, 2669)}


def _fake_raw(n_cells: int = 40) -> loader.RawSession:
    """A small session with the real layout: two 9,500-frame segments and the real TASK windows."""
    rng = np.random.default_rng(0)
    state = np.ones(19000)
    for sp in loader.SPLITS.values():
        state[sp.task_start:sp.task_stop] = 0.0
    state[7305] = 0.0319  # interpolation artefact, as in the file
    spike = (rng.random((n_cells, 19000)) < 0.02).astype(np.float32)
    spike[3, 5481:7306] += 1.0  # cell 3 is the most active in Split A TASK
    return loader.RawSession(spike=spike, state=state, boundary_ind=np.array([9500, 19000]),
                             atlas_id=np.arange(n_cells))


def _write_mat(path, raw: loader.RawSession, drop: str | None = None) -> None:
    d = {
        "spike": raw.spike.astype(np.float64),
        "state": {"state": raw.state, "EMG": np.zeros_like(raw.state)},
        "frame": {"boundary_ind": raw.boundary_ind.astype(np.float64)},
        "ROIs": {"atlasID": raw.atlas_id.astype(np.uint16), "Centroid": np.zeros((raw.atlas_id.size, 2))},
    }
    if drop == "spike":
        del d["spike"]
    elif drop:
        var, sub = drop.split(".")
        del d[var][sub]
    sio.savemat(path, d)


# ---- synthetic file ---------------------------------------------------------------------------


def test_contract_fields_and_split_bounds(tmp_path):
    p = tmp_path / "sleep_data.mat"
    _write_mat(p, _fake_raw())
    a, b = loader.load_sessions(p, n_cells=10, cache_dir=tmp_path / "cache")
    for rec, sid in ((a, "A"), (b, "B")):
        assert rec.deconv.shape == (10, 9500) and rec.deconv.dtype == np.float64
        assert rec.fs == 7.65 and rec.mouse_id == "mouse05" and rec.session_id == f"mouse05_split{sid}"
        assert rec.session_type == "spontaneous" and rec.stim_frames is None
        assert rec.cell_id.shape == (10,)
        # TASK is one contiguous block; PRE before it, POST after it, nothing else.
        task = np.flatnonzero(rec.epoch == "TASK")
        assert np.all(np.diff(task) == 1)
        assert np.all(rec.epoch[: task[0]] == "PRE") and np.all(rec.epoch[task[-1] + 1:] == "POST")
    assert "3" in a.cell_id  # the most active TASK cell is selected
    assert a.cell_id.tolist() == b.cell_id.tolist()  # same cells in both splits (M2)
    assert (tmp_path / "cache").exists() and any((tmp_path / "cache").iterdir())


def test_cache_roundtrip_is_identical(tmp_path):
    p = tmp_path / "sleep_data.mat"
    _write_mat(p, _fake_raw())
    first = loader.load_sessions(p, cache_dir=tmp_path / "cache")
    second = loader.load_sessions(p, cache_dir=tmp_path / "cache")  # from the .npz
    for r1, r2 in zip(first, second):
        np.testing.assert_array_equal(r1.deconv, r2.deconv)
        np.testing.assert_array_equal(r1.cell_id, r2.cell_id)


@pytest.mark.parametrize("field", ["spike", "state.state", "frame.boundary_ind", "ROIs.atlasID"])
def test_missing_required_field_stops_with_clear_message(tmp_path, field):
    p = tmp_path / "sleep_data.mat"
    _write_mat(p, _fake_raw(), drop=field)
    with pytest.raises(loader.LoaderError, match=f"required field '{field}' is missing"):
        loader.load_sessions(p, cache_dir=None)


def test_missing_file_stops_with_clear_message(tmp_path):
    with pytest.raises(loader.LoaderError, match="file not found"):
        loader.load_sessions(tmp_path / "nope.mat")


def test_stage_mapping():
    got = loader.sleep_stages(np.array([0, 0.5, 1, 2, 0.0319]))
    assert got.tolist() == ["wake", "wake", "NREM", "REM", "unscored"]


def test_cell_selection_over_union_of_task_frames():
    rng = np.random.default_rng(1)
    X = rng.random((500, 651))
    X[7] += 5.0
    got = loader.select_cells(X, 300)
    assert got.size == 300 and 7 in got and np.all(np.diff(got) > 0)
    assert loader.select_cells(X, None).size == 500
    assert loader.task_frames(("A", "B")).size == 1825 + 651


# ---- real file --------------------------------------------------------------------------------

needs_data = pytest.mark.skipif(not loader.DEFAULT_DATA.exists(), reason=f"{loader.DEFAULT_DATA} not present")


@pytest.fixture(scope="module")
def real_sessions():
    return {r.session_id[-1]: r for r in loader.load_sessions(n_cells=300)}


@needs_data
@pytest.mark.parametrize("split", ["A", "B"])
def test_real_frame_counts_match_vetting_report(real_sessions, split):
    rec = real_sessions[split]
    pre, task_all, task_scored, post = EXPECTED[split]
    assert int(analysis_mask(rec, "PRE").sum()) == pre
    assert int((rec.epoch == "TASK").sum()) == task_all
    assert int(analysis_mask(rec, "TASK").sum()) == task_scored
    assert int(analysis_mask(rec, "POST").sum()) == post
    assert set(rec.sleep_stage[rec.epoch == "TASK"]) <= {"wake", "unscored"}


@needs_data
def test_real_same_300_cells_in_both_splits(real_sessions):
    a, b = real_sessions["A"], real_sessions["B"]
    assert a.deconv.shape == b.deconv.shape == (300, 9500)
    assert a.cell_id.tolist() == b.cell_id.tolist()
    for rec in (a, b):
        assert np.all(rec.deconv >= 0) and np.isfinite(rec.deconv).all()
    # TASK frames >= 5 x cells holds in A (1824 >= 1500) and fails in B (651 < 1500), by design.
    assert int(analysis_mask(a, "TASK").sum()) >= 1500 > int(analysis_mask(b, "TASK").sum())


@needs_data
def test_real_split_b_not_eligible_for_m3_m4_with_reason(real_sessions):
    from toolbox import m3_pca, m4_ica

    for mod in (m3_pca, m4_ica):
        req = mod.check_requirements(real_sessions["B"])
        assert not req.eligible and "TASK" in req.reason, req
