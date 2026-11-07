"""T-M4-1 to T-M4-4 (plans/engineer-b.md section 5)."""

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

from conftest import N_SHUFFLES_COUNTED, at_least, at_most, n_seeds, report
from toolbox.assemblies import AssemblyParams, significant_subspace
from toolbox.controls import scenario
from toolbox.m4_ica import ICAParams, ica_weights
from toolbox.m4_ica import run as run_m4
from toolbox.nulls import rng_for
from toolbox.synth import make_session

PARAMS = AssemblyParams(n_shuffles=N_SHUFFLES_COUNTED)


def _matched_abs_cos(W, truth):
    cos = np.abs(truth.T @ W)  # (n_true, n_found), unit columns
    r, c = linear_sum_assignment(-cos)
    return float(cos[r, c].sum() / truth.shape[1])


@pytest.mark.xfail(strict=False, reason="recorded failure, see JOURNAL.md")
def test_t_m4_1_overlap_ica_beats_pca():
    overlap = [np.arange(0, 8), np.arange(4, 12)]  # 50% member overlap
    rec = make_session(assemblies=overlap, seed=0)
    sub = significant_subspace(rec, PARAMS, seed=0)
    assert sub.n_sig == 2, sub.n_sig
    truth = np.zeros((len(sub.kept_cells), 2))
    for j, members in enumerate(overlap):
        truth[np.isin(sub.kept_cells, members), j] = 1.0
    truth /= np.linalg.norm(truth, axis=0)
    W = ica_weights(sub, ICAParams(), rng_for(0, rec.session_id, "ica"))
    ica, pca = _matched_abs_cos(W, truth), _matched_abs_cos(sub.V_sig, truth)
    print(f"[T-M4-1] matched mean |cos|: ICA {ica:.3f}, PCA {pca:.3f}")
    assert ica >= 0.9
    assert pca < 0.8


def _runs(name, scale):
    n = n_seeds(scale)
    return [run_m4(scenario(name, seed=s, tau_s=1.0), seed=s, params=PARAMS) for s in range(n)], n


def test_t_m4_2_controls(scale):
    pos, n = _runs("positive", scale)
    hits = sum(r.eligible and r.score > 0 and r.p_n1 < 0.05 for r in pos)
    report("T-M4-2 positive", scale, hits, n, "at least")

    neg2, _ = _runs("no_sleep_coactivity", scale)
    fp2 = sum(r.eligible and r.p_n1 < 0.05 for r in neg2)
    report("T-M4-2 no_sleep_coactivity", scale, fp2, n, "at most")

    neg3, _ = _runs("pre_existing", scale)
    fp3 = sum(r.eligible and r.details["p_blockswap"] < 0.05 for r in neg3)
    report("T-M4-2 pre_existing p_blockswap", scale, fp3, n, "at most")
    report("T-M4-2 pre_existing p_n1 (info)", scale, sum(r.eligible and r.p_n1 < 0.05 for r in neg3), n, "info")

    neg4, _ = _runs("other_assemblies", scale)
    fp4 = sum(r.eligible and r.p_n1 < 0.05 for r in neg4)
    report("T-M4-2 other_assemblies", scale, fp4, n, "at most")

    noise, _ = _runs("noise_only", scale)
    inel = sum((not r.eligible) and "N1 bound" in r.reason for r in noise)
    report("T-M4-2 noise_only", scale, inel, n, "at least")

    assert hits >= at_least(scale, 47)
    assert fp2 <= at_most(scale, 5)
    assert fp3 <= at_most(scale, 5)
    assert fp4 <= at_most(scale, 5)
    assert inel >= at_least(scale, 45)


def test_t_m4_3_requirement():
    rec = make_session(assemblies=[np.arange(0, 8)], seed=0)
    r = run_m4(rec, seed=0, params=PARAMS)
    assert not r.eligible
    assert "1 < 2 significant components" in r.reason, r.reason


def test_t_m4_4_determinism_and_sign():
    rec = scenario("positive", seed=2, tau_s=1.0)
    sub = significant_subspace(rec, PARAMS, seed=2)
    W1 = ica_weights(sub, ICAParams(), rng_for(2, rec.session_id, "ica"))
    W2 = ica_weights(sub, ICAParams(), rng_for(2, rec.session_id, "ica"))
    assert np.array_equal(W1, W2)
    np.testing.assert_allclose(np.linalg.norm(W1, axis=0), 1.0, atol=1e-12)
    for j in range(W1.shape[1]):
        assert W1[np.argmax(np.abs(W1[:, j])), j] > 0
    assert run_m4(rec, seed=2, params=PARAMS).to_json() == run_m4(rec, seed=2, params=PARAMS).to_json()
