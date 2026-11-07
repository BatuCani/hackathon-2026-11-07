"""T-N1-1 to T-N1-9 (plans/engineer-b.md section 5)."""

import numpy as np
import pytest

from conftest import N_SHUFFLES_COUNTED, at_least, at_most, n_seeds, report
from reactivation.assemblies import correlation, eigh_desc, n1_eigen_bound, zscore
from reactivation.contract import analysis_mask
from reactivation.nulls import circular_shift, n1_offsets, n1_pvalue, n1_surrogates, rng_for
from reactivation.synth import make_session

ASSEMBLIES = [np.arange(0, 8), np.arange(8, 16), np.arange(16, 24)]


def _task_z(rec):
    return zscore(rec.deconv[:, analysis_mask(rec, "TASK")])


def _random_matrix(seed=0, n=20, b=1000):
    return np.random.default_rng(seed).standard_normal((n, b))


def test_t_n1_1_shift_keeps_values():
    X = _random_matrix()
    offs = n1_offsets(*X.shape, n_shuffles=1, rng=np.random.default_rng(1))[0]
    Xs = circular_shift(X, offs)
    assert np.array_equal(np.sort(Xs, 1), np.sort(X, 1))


def test_t_n1_2_shift_keeps_autocorrelation():
    X = _random_matrix()
    offs = n1_offsets(*X.shape, n_shuffles=1, rng=np.random.default_rng(1))[0]
    Xs = circular_shift(X, offs)

    def circ_ac(M, lag):
        return np.sum(M * np.roll(M, lag, axis=1), axis=1) / np.sum(M * M, axis=1)

    for lag in range(1, 6):
        np.testing.assert_allclose(circ_ac(Xs, lag), circ_ac(X, lag), rtol=0, atol=1e-12)


def test_t_n1_3_offsets():
    n_cells, n_frames = 30, 500
    for min_shift in (1, 50):
        offs = n1_offsets(n_cells, n_frames, 500, np.random.default_rng(0), min_shift=min_shift)
        assert offs.dtype == np.int64 and offs.shape == (500, n_cells)
        assert offs.min() >= min_shift and offs.max() <= n_frames - min_shift
    with pytest.raises(ValueError):
        n1_offsets(5, 2, 10, np.random.default_rng(0), min_shift=1)


def test_t_n1_4_coactivity_broken():
    rec = make_session(assemblies=ASSEMBLIES, tau_s=0.0, seed=0)
    Z = _task_z(rec)
    members = ASSEMBLIES[0]
    iu = np.triu_indices(len(members), 1)
    before = correlation(Z[members])[iu].mean()
    offs = n1_offsets(*Z.shape, n_shuffles=1, rng=rng_for(0, "t", "n1"))[0]
    after = correlation(circular_shift(Z, offs)[members])[iu].mean()
    print(f"[T-N1-4] mean member-pair r: before {before:.3f}, after one shift {after:.4f}")
    assert before > 0.1
    assert abs(after) < 0.01


def test_t_n1_5_seeds():
    a = n1_offsets(10, 100, 5, rng_for(0, "s1", "purpose"))
    b = n1_offsets(10, 100, 5, rng_for(0, "s1", "purpose"))
    c = n1_offsets(10, 100, 5, rng_for(0, "s1", "other"))
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_t_n1_6_pvalue():
    null = np.arange(500, dtype=float)
    assert n1_pvalue(1000.0, null) == pytest.approx(1 / 501)
    assert n1_pvalue(-1.0, null) == 1.0
    assert n1_pvalue(499.0, null) == pytest.approx(2 / 501)  # tie counts as >=


def test_n1_surrogates_count():
    X = _random_matrix()
    assert sum(1 for _ in n1_surrogates(X, 7, np.random.default_rng(0))) == 7


def test_t_n1_7_bound_matches_analytical_for_independent_bins():
    rec = make_session(assemblies=(), tau_s=0.0, seed=0)
    eb = n1_eigen_bound(_task_z(rec), n_shuffles=500, quantile=0.95, rng=rng_for(0, rec.session_id, "eigen_bound"))
    mp = (1 + np.sqrt(50 / 6000)) ** 2
    print(f"[T-N1-7] N1 bound {eb.bound:.4f}, mean of null max {eb.null_max_eigs.mean():.4f}, MP {mp:.4f}")
    assert eb.mp_bound == pytest.approx(mp)
    assert abs(eb.bound - 1.191) <= 0.02


def test_t_n1_8_analytical_bound_too_lenient_for_calcium(scale):
    n = n_seeds(scale)
    n1_any, mp_many = 0, 0
    for seed in range(n):
        rec = make_session(assemblies=(), tau_s=1.0, seed=seed, session_id=f"synth-{seed}")
        Z = _task_z(rec)
        eb = n1_eigen_bound(Z, n_shuffles=N_SHUFFLES_COUNTED, quantile=0.95, rng=rng_for(seed, rec.session_id, "eigen_bound"))
        eig, _ = eigh_desc(correlation(Z))
        n1_any += int(np.sum(eig > eb.bound) >= 1)
        mp_many += int(np.sum(eig > eb.mp_bound) >= 5)
    report("T-N1-8 N1>=1", scale, n1_any, n, "at most")
    report("T-N1-8 MP>=5", scale, mp_many, n, "at least")
    assert n1_any <= at_most(scale, 5)
    assert mp_many >= at_least(scale, 45)


@pytest.mark.parametrize("tau_s", [0.0, 1.0])
def test_t_n1_9_planted_recovery(scale, tau_s):
    n = n_seeds(scale)
    hits = 0
    for seed in range(n):
        rec = make_session(assemblies=ASSEMBLIES, tau_s=tau_s, seed=seed, session_id=f"synth-{seed}")
        Z = _task_z(rec)
        eb = n1_eigen_bound(Z, n_shuffles=N_SHUFFLES_COUNTED, quantile=0.95, rng=rng_for(seed, rec.session_id, "eigen_bound"))
        eig, _ = eigh_desc(correlation(Z))
        hits += int(np.sum(eig > eb.bound) == 3)
    report(f"T-N1-9 tau={tau_s}", scale, hits, n, "at least")
    assert hits >= at_least(scale, 47)
