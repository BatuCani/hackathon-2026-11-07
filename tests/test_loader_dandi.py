"""Loader for DANDI:000044 (Grosmark & Buzsaki 2016), tested on a tiny fake NWB file.

The fake file holds only the fields the loader reads, with the layout seen in the real
Buddy session (units ragged spike_times + cell_type, intervals/epochs PRE/MAZE/POST,
processing/behavior/sleep_states_buzcode WAKE/NREM/REM).
"""

import h5py
import numpy as np
import pytest

from toolbox.contract import analysis_mask
from toolbox.loader_dandi import load_dandi44


def _strings(group, name, values):
    group.create_dataset(name, data=np.array(values, dtype=object), dtype=h5py.string_dtype())


def _fake_nwb(path, *, drop=None):
    spikes = [np.array([0.05, 0.15, 0.16, 5.01]), np.array([2.0, 2.05]), np.array([9.95])]
    with h5py.File(path, "w") as f:
        f["general/session_id"] = "Fake-01012020"
        f["general/subject/subject_id"] = "Fake"
        ep = f.create_group("intervals/epochs")
        ep["start_time"], ep["stop_time"] = [0.0, 4.0, 6.0], [4.0, 6.0, 10.0]
        _strings(ep, "label", ["PRE", "MAZE", "POST"])
        st = f.create_group("processing/behavior/sleep_states_buzcode")
        st["start_time"], st["stop_time"] = [0.0, 1.0, 3.0, 6.0, 9.0], [1.0, 3.0, 4.0, 9.0, 10.0]
        _strings(st, "label", ["WAKE", "NREM", "REM", "NREM", "WAKE"])
        u = f.create_group("units")
        u["spike_times"] = np.concatenate(spikes)
        u["spike_times_index"] = np.cumsum([len(s) for s in spikes])
        u["id"] = [0, 1, 2]
        _strings(u, "cell_type", ["pyramidal cell", "interneuron", "pyramidal cell"])
        if drop:
            del f[drop]


def test_binning_epochs_states(tmp_path):
    p = tmp_path / "fake.nwb"
    _fake_nwb(p)
    rec = load_dandi44(p, bin_s=0.1, cell_types=None)
    assert rec.deconv.shape == (3, 100) and rec.deconv.dtype == np.float64
    assert rec.fs == pytest.approx(10.0)
    assert rec.deconv[0, 0] == 1 and rec.deconv[0, 1] == 2 and rec.deconv[0, 50] == 1
    assert rec.deconv[1, 20] == 2 and rec.deconv[2, 99] == 1
    np.testing.assert_array_equal(rec.deconv.sum(1), [4, 2, 1])
    assert list(rec.epoch[[0, 39, 40, 59, 60, 99]]) == ["PRE", "PRE", "TASK", "TASK", "POST", "POST"]
    assert list(rec.sleep_stage[[0, 10, 30, 45, 60, 95]]) == ["wake", "NREM", "REM", "unscored", "NREM", "wake"]
    assert analysis_mask(rec, "PRE").sum() == 20 and analysis_mask(rec, "POST").sum() == 30
    assert analysis_mask(rec, "TASK").sum() == 0  # MAZE frames have no buzcode label -> unscored
    assert rec.session_id == "Fake-01012020" and rec.mouse_id == "Fake"
    assert list(rec.cell_id) == ["0", "1", "2"]
    assert rec.session_type == "training" and rec.stim_frames is None


def test_cell_type_filter(tmp_path):
    p = tmp_path / "fake.nwb"
    _fake_nwb(p)
    rec = load_dandi44(p, bin_s=0.1)  # default: pyramidal cells only
    assert list(rec.cell_id) == ["0", "2"]
    np.testing.assert_array_equal(rec.deconv.sum(1), [4, 1])


def test_task_unlabelled_frames_count_as_wake(tmp_path):
    p = tmp_path / "fake.nwb"
    _fake_nwb(p)
    rec = load_dandi44(p, bin_s=0.1, task_unscored_as_wake=True)
    assert analysis_mask(rec, "TASK").sum() == 20


@pytest.mark.parametrize("drop", ["intervals/epochs", "units/spike_times", "processing/behavior/sleep_states_buzcode"])
def test_missing_field_stops_with_clear_message(tmp_path, drop):
    p = tmp_path / "fake.nwb"
    _fake_nwb(p, drop=drop)
    with pytest.raises(ValueError, match=drop.split("/")[-1]):
        load_dandi44(p)
