"""T-M3-1 to T-M3-8 (plans/engineer-b.md section 5).

Controls use tau_s = 1 (calcium-like autocorrelation) for every scenario, the
stress case of the brief; the plan states tau_s = 1 only for T-M3-1 and T-M3-5.
"""

import numpy as np
import pytest

from conftest import N_SHUFFLES_COUNTED, at_least, at_most, n_seeds, report
from reactivation.assemblies import AssemblyParams
from reactivation.controls import scenario
from reactivation.m3_pca import run as run_m3
from reactivation.synth import make_session

PARAMS = AssemblyParams(n_shuffles=N_SHUFFLES_COUNTED)


def _runs(name, scale, run=run_m3):
    n = n_seeds(scale)
    return [run(scenario(name, seed=s, tau_s=1.0), seed=s, params=PARAMS) for s in range(n)], n


def test_t_m3_1_positive_control(scale):
    res, n = _runs("positive", scale)
    hits = sum(r.eligible and r.score > 0 and r.p_n1 < 0.05 for r in res)
    report("T-M3-1", scale, hits, n, "at least")
    assert hits >= at_least(scale, 47)


def test_t_m3_2_no_sleep_coactivity(scale):
    res, n = _runs("no_sleep_coactivity", scale)
    fp = sum(r.eligible and r.p_n1 < 0.05 for r in res)
    report("T-M3-2", scale, fp, n, "at most")
    assert fp <= at_most(scale, 5)


def test_t_m3_3_pre_existing(scale):
    res, n = _runs("pre_existing", scale)
    fp_bs = sum(r.eligible and r.details["p_blockswap"] < 0.05 for r in res)
    fp_n1 = sum(r.eligible and r.p_n1 < 0.05 for r in res)
    report("T-M3-3 p_blockswap", scale, fp_bs, n, "at most")
    report("T-M3-3 p_n1 (reported, not gated)", scale, fp_n1, n, "info")
    assert fp_bs <= at_most(scale, 5)


def test_t_m3_4_other_assemblies(scale):
    res, n = _runs("other_assemblies", scale)
    fp = sum(r.eligible and r.p_n1 < 0.05 for r in res)
    report("T-M3-4", scale, fp, n, "at most")
    assert fp <= at_most(scale, 5)


def test_t_m3_5_noise_only(scale):
    res, n = _runs("noise_only", scale)
    inel = sum((not r.eligible) and "N1 bound" in r.reason for r in res)
    report("T-M3-5", scale, inel, n, "at least")
    assert inel >= at_least(scale, 45)


def test_t_m3_6_ineligibility():
    few = make_session(n_cells=5, seed=0)
    r = run_m3(few, seed=0, params=PARAMS)
    assert not r.eligible and "cells" in r.reason, r.reason
    assert np.isnan(r.score) and np.isnan(r.p_n1)

    no_post = make_session(frames={"PRE": 5700, "TASK": 6000, "POST": 0}, seed=0)
    r = run_m3(no_post, seed=0, params=PARAMS)
    assert not r.eligible and "POST NREM" in r.reason, r.reason
    assert any("POST NREM" in m for m in r.missing)

    nan = make_session(seed=0)
    nan.deconv[3, 100] = np.nan
    r = run_m3(nan, seed=0, params=PARAMS)
    assert not r.eligible and "finite" in r.reason, r.reason


def test_t_m3_7_determinism():
    rec = scenario("positive", seed=1, tau_s=1.0)
    a = run_m3(rec, seed=1, params=PARAMS).to_json()
    b = run_m3(rec, seed=1, params=PARAMS).to_json()
    assert a == b


def test_t_m3_8_reversal(scale):
    res, n = _runs("reversed", scale)
    hits = sum(r.eligible and r.score < 0 and r.p_n1 > 0.95 for r in res)
    report("T-M3-8", scale, hits, n, "at least")
    assert hits >= at_least(scale, 47)


def test_result_json_fields():
    r = run_m3(scenario("positive", seed=0, tau_s=1.0), seed=0, params=PARAMS)
    assert r.method_id == "M3" and r.n_shuffles == N_SHUFFLES_COUNTED and r.seed == 0
    for key in ("n_sig", "eigenvalues_top10", "bound", "mp_bound", "delta_k", "mean_R_pre",
                "mean_R_post", "p_n1_post_alone", "p_n1_pre_alone", "p_blockswap", "dropped_cells"):
        assert key in r.details, key
    assert r.score == pytest.approx(np.mean(r.details["delta_k"]))
