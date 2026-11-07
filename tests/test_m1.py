"""M1 controls: positive, noise, pre-existing, rate-confound.

D1 matches numpy Pearson on the strict upper triangle.
Yes means eligible, score > 0 and p_n1 < 0.05.

Sessions use the plan default (N=50, about 4000 NREM frames).
Shorter traces leave the assembly pairs under the sampling noise of the full upper triangle,
so a correct D1 does not clear p < 0.05 there.
"""

import math
from dataclasses import replace

import numpy as np
import pytest

from toolbox.contract import analysis_mask
from toolbox.controls import scenario
from toolbox.m1_pair_corr import M1Params, check_requirements, run
from toolbox.synth import make_session

PARAMS = M1Params(n_shuffles=80)
SEEDS = range(8)


def _yes(result) -> bool:
    return bool(result.eligible and result.score > 0 and result.p_n1 < 0.05)


def _scenario(name: str, seed: int, **kwargs):
    kwargs.setdefault("tau_s", 1.0)
    return scenario(name, seed=seed, **kwargs)


def _scale_post(rec, gains: np.ndarray):
    X = np.array(rec.deconv, dtype=np.float64, copy=True)
    X[:, analysis_mask(rec, "POST")] *= np.asarray(gains, dtype=np.float64)
    return replace(rec, deconv=X)


def _numpy_d1(rec) -> float:
    keep = np.ones(rec.deconv.shape[0], dtype=bool)
    blocks = {}
    for ep in ("PRE", "TASK", "POST"):
        blocks[ep] = np.asarray(rec.deconv[:, analysis_mask(rec, ep)], dtype=np.float64)
        keep &= blocks[ep].std(axis=1) > 0
    vectors = {}
    for ep, X in blocks.items():
        C = np.corrcoef(X[keep])
        vectors[ep] = C[np.triu_indices(int(keep.sum()), k=1)]
    r_post = np.corrcoef(vectors["TASK"], vectors["POST"])[0, 1]
    r_pre = np.corrcoef(vectors["TASK"], vectors["PRE"])[0, 1]
    return float(r_post - r_pre)


def test_d1_matches_numpy_corrcoef():
    rec = _scenario("positive", 1, tau_s=0.0)
    result = run(rec, seed=1, params=PARAMS)
    assert result.eligible
    assert result.score == pytest.approx(_numpy_d1(rec), abs=1e-8)
    assert result.details["r_task_post"] - result.details["r_task_pre"] == pytest.approx(result.score, abs=1e-12)


def test_positive_control():
    hits = sum(_yes(run(_scenario("positive", s), seed=s, params=PARAMS)) for s in SEEDS)
    assert hits >= 7, hits


def test_noise_control():
    hits = sum(_yes(run(_scenario("noise_only", s), seed=s, params=PARAMS)) for s in SEEDS)
    assert hits <= 2, hits


def test_pre_existing_control():
    hits = sum(_yes(run(_scenario("pre_existing", s), seed=s, params=PARAMS)) for s in SEEDS)
    assert hits <= 2, hits


def test_rate_confound_gain_does_not_change_d1_or_p():
    rec = _scenario("pre_existing", 0)
    gains = np.linspace(2.0, 12.0, rec.deconv.shape[0])[:, None]
    scaled = _scale_post(rec, gains)
    base = run(rec, seed=0, params=PARAMS)
    confound = run(scaled, seed=0, params=PARAMS)
    assert base.eligible and confound.eligible
    assert confound.score == pytest.approx(base.score, abs=1e-8)
    assert confound.p_n1 == pytest.approx(base.p_n1, abs=1e-12)
    assert confound.details["r_task_post"] == pytest.approx(base.details["r_task_post"], abs=1e-8)


def test_rate_confound_extra_independent_spikes_are_not_a_yes():
    hits = 0
    for s in SEEDS:
        rec = _scenario("no_sleep_coactivity", s)
        rng = np.random.default_rng(1000 + s)
        X = np.array(rec.deconv, dtype=np.float64, copy=True)
        mask = analysis_mask(rec, "POST")
        n = int(mask.sum())
        extra = (rng.random((X.shape[0], n)) < 0.2) * rng.lognormal(0.0, 0.5, (X.shape[0], n))
        X[:, mask] += extra
        X[:, mask] *= np.linspace(3.0, 9.0, X.shape[0])[:, None]
        boosted = replace(rec, deconv=X)
        hits += _yes(run(boosted, seed=s, params=PARAMS))
    assert hits <= 2, hits


def test_ineligible_short_post_and_nan_and_duplicate_cells():
    short = make_session(frames={"PRE": 500, "TASK": 400, "POST": 100}, nrem_fraction=1.0, seed=0)
    req = check_requirements(short)
    assert not req.eligible and "POST NREM" in req.reason
    assert any("POST NREM" in item for item in req.missing)
    result = run(short, seed=0)
    assert not result.eligible
    assert math.isnan(result.score) and math.isnan(result.p_n1)
    assert result.n_shuffles == 500

    dirty = make_session(seed=0)
    dirty.deconv[1, 10] = np.nan
    nan_result = run(dirty, seed=0)
    assert not nan_result.eligible and "non-finite" in nan_result.reason

    dup = _scenario("positive", 2, tau_s=0.0)
    dup.cell_id[1] = dup.cell_id[0]
    dup_result = run(dup, seed=2, params=PARAMS)
    assert not dup_result.eligible and "same cells" in dup_result.reason


def test_determinism_and_null_pvalue_form():
    rec = _scenario("positive", 3, tau_s=0.0)
    params = M1Params(n_shuffles=40)
    first = run(rec, seed=3, params=params)
    assert first.to_json() == run(rec, seed=3, params=params).to_json()
    assert first.to_json() != run(rec, seed=4, params=params).to_json()
    unit = (params.n_shuffles + 1) * first.p_n1
    assert unit == pytest.approx(round(unit), abs=1e-8)
    assert first.method_id == "M1"
    assert first.params["n_shuffles"] == 40
