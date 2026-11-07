"""T-S1 to T-S3 (plans/engineer-b.md section 5)."""

import numpy as np

from toolbox.contract import Recording, analysis_mask
from toolbox.synth import make_session

ASSEMBLIES = [np.arange(0, 8), np.arange(8, 16), np.arange(16, 24)]


def _lag1(x: np.ndarray) -> float:
    x = x - x.mean()
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x))


def test_t_s1_contract_and_nrem_fraction():
    rec = make_session(assemblies=ASSEMBLIES, seed=0)
    assert isinstance(rec, Recording)
    n_frames = 5700 + 6000 + 5700
    assert rec.deconv.dtype == np.float64 and rec.deconv.shape == (50, n_frames)
    assert rec.sleep_stage.shape == (n_frames,) and rec.sleep_stage.dtype.kind == "U"
    assert rec.epoch.shape == (n_frames,) and rec.epoch.dtype.kind == "U"
    assert set(np.unique(rec.sleep_stage)) <= {"wake", "NREM", "REM", "unscored"}
    assert set(np.unique(rec.epoch)) <= {"PRE", "TASK", "POST", "none"}
    assert rec.cell_id.shape == (50,) and len(set(rec.cell_id)) == 50
    assert rec.fs == 10.0
    assert rec.session_type in {"baseline", "training", "test", "spontaneous"}
    assert np.all(rec.sleep_stage[rec.epoch == "TASK"] == "wake")
    for ep in ("PRE", "POST"):
        sel = rec.epoch == ep
        frac = np.mean(rec.sleep_stage[sel] == "NREM")
        assert abs(frac - 0.7) <= 0.02, (ep, frac)
        assert analysis_mask(rec, ep).sum() == np.sum(sel & (rec.sleep_stage == "NREM"))


def test_t_s2_determinism():
    a = make_session(assemblies=ASSEMBLIES, tau_s=1.0, seed=3)
    b = make_session(assemblies=ASSEMBLIES, tau_s=1.0, seed=3)
    c = make_session(assemblies=ASSEMBLIES, tau_s=1.0, seed=4)
    assert np.array_equal(a.deconv, b.deconv)
    assert np.array_equal(a.sleep_stage, b.sleep_stage)
    assert not np.array_equal(a.deconv, c.deconv)


def test_t_s3_autocorrelation():
    slow = make_session(tau_s=1.0, seed=0)
    white = make_session(tau_s=0.0, seed=0)
    lag_slow = np.median([_lag1(r) for r in slow.deconv])
    lag_white = np.median([_lag1(r) for r in white.deconv])
    print(f"[T-S3] median lag-1: tau_s=1 -> {lag_slow:.3f} (theory 0.905); tau_s=0 -> {lag_white:.4f}")
    assert lag_slow >= 0.8
    assert abs(lag_white) < 0.05
