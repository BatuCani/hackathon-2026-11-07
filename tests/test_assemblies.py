"""T-A1 to T-A5 (plans/engineer-b.md section 5)."""

import numpy as np

from toolbox.assemblies import (
    AssemblyParams,
    correlation,
    mean_strength,
    projector,
    reactivation_strength,
    zscore,
)
from toolbox.m3_pca import run as run_m3
from toolbox.synth import make_session


def test_t_a1_hand_example():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(4)
    v /= np.linalg.norm(v)
    Z = rng.standard_normal((4, 30))
    R = reactivation_strength(v[:, None], Z)[0]
    explicit = np.array(
        [sum(v[k] * v[l] * Z[k, t] * Z[l, t] for k in range(4) for l in range(4) if k != l) for t in range(30)]
    )
    np.testing.assert_allclose(R, explicit, rtol=0, atol=1e-12)
    P = projector(v)
    assert np.all(np.diag(P) == 0)
    np.testing.assert_allclose(R, np.einsum("it,ij,jt->t", Z, P, Z), rtol=0, atol=1e-12)


def test_t_a2_closed_form():
    rng = np.random.default_rng(1)
    Z = zscore(rng.standard_normal((12, 400)))
    V = np.linalg.qr(rng.standard_normal((12, 3)))[0]
    C = correlation(Z)
    expected = np.array([V[:, k] @ C @ V[:, k] - 1 for k in range(3)])
    np.testing.assert_allclose(reactivation_strength(V, Z).mean(axis=1), expected, rtol=0, atol=1e-10)
    np.testing.assert_allclose(mean_strength(V, Z), expected, rtol=0, atol=1e-10)


def test_t_a3_rate_invariance():
    rng = np.random.default_rng(2)
    X = rng.gamma(1.0, 1.0, (10, 300))
    a = rng.uniform(0.1, 10, (10, 1))
    b = rng.uniform(-5, 5, (10, 1))
    V = np.linalg.qr(rng.standard_normal((10, 2)))[0]
    np.testing.assert_allclose(
        reactivation_strength(V, zscore(a * X + b)), reactivation_strength(V, zscore(X)), rtol=0, atol=1e-10
    )


def test_t_a4_correlation():
    X = np.random.default_rng(3).standard_normal((15, 200))
    np.testing.assert_allclose(correlation(zscore(X)), np.corrcoef(X), rtol=0, atol=1e-12)


def test_t_a5_zero_variance_cell():
    rec = make_session(assemblies=[np.arange(0, 8), np.arange(8, 16), np.arange(16, 24)], seed=0)
    rec.deconv[40, :] = 0.0
    res = run_m3(rec, seed=0, params=AssemblyParams(n_shuffles=50))
    assert res.eligible, res.reason
    assert res.details["dropped_cells"] == [str(rec.cell_id[40])]
    assert res.details["n_cells_kept"] == 49
