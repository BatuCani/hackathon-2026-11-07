"""M2 EV / REV tests: hand-checked formula, requirements, and positive / negative controls."""

import math

import numpy as np
import pytest

from conftest import N_SHUFFLES_COUNTED, at_least, at_most, n_seeds, report
from toolbox import m2_ev_rev as m2
from toolbox.controls import scenario


def _upper(C):
    return np.asarray(C)[np.triu_indices(3, k=1)]


def test_ev_rev_formula_by_hand():
    # r_T,POST = 0.8, r_T,PRE = 0.5, r_PRE,POST = 0.5
    # EV  = ((0.8 - 0.5*0.5) / sqrt(0.75*0.75))^2 = (0.55/0.75)^2 = 0.537777...
    # REV = ((0.5 - 0.8*0.5) / sqrt(0.36*0.75))^2 = 0.01/0.27  = 0.037037...
    e, rev = m2.ev_rev(0.8, 0.5, 0.5)
    assert e == pytest.approx((0.55 / 0.75) ** 2, abs=1e-12)
    assert rev == pytest.approx(0.01 / 0.27, abs=1e-12)
    assert e - rev == pytest.approx(0.5007407407, abs=1e-9)


def test_3x3_matrices_by_hand():
    # Three cells -> three pairs (C01, C02, C12).
    C_T = [[1, 0.1, 0.2], [0.1, 1, 0.3], [0.2, 0.3, 1]]      # (0.1, 0.2, 0.3)
    C_POST = [[1, 0.1, 0.3], [0.1, 1, 0.2], [0.3, 0.2, 1]]   # (0.1, 0.3, 0.2)
    C_PRE = [[1, 0.0, 0.0], [0.0, 1, 0.3], [0.0, 0.3, 1]]    # (0.0, 0.0, 0.3)
    # Centered: T (-.1, 0, .1), POST (-.1, .1, 0), PRE (-.1, -.1, .2)
    # r_T,POST = .01 / (sqrt(.02) sqrt(.02)) = 0.5
    # r_T,PRE  = .03 / (sqrt(.02) sqrt(.06)) = sqrt(3)/2
    # r_PRE,POST = (.01 - .01) / ... = 0
    out = m2.d2_from_vectors(_upper(C_T), _upper(C_PRE), _upper(C_POST))
    assert out["r_task_post"] == pytest.approx(0.5)
    assert out["r_task_pre"] == pytest.approx(math.sqrt(3) / 2)
    assert out["r_pre_post"] == pytest.approx(0.0, abs=1e-12)
    # EV = (0.5 - 0)^2 / ((1 - 3/4)(1 - 0)) = 1 ; REV = (3/4) / ((1 - 1/4)(1)) = 1.
    # With 3 pairs the centered vectors span 2 dimensions, so the partial correlation is always +-1:
    # this is why min_cells = 4.
    assert out["ev"] == pytest.approx(1.0)
    assert out["rev"] == pytest.approx(1.0)
    assert out["d2"] == pytest.approx(0.0, abs=1e-9)


def test_pair_corr_vec_matches_numpy():
    X = np.random.default_rng(0).normal(size=(5, 200))
    C = np.corrcoef(X)
    assert np.allclose(m2.pair_corr_vec(X), C[np.triu_indices(5, k=1)])


def test_requirements_fail_with_numbers():
    rec = scenario("positive", seed=0, frames={"PRE": 300, "TASK": 500, "POST": 2000}, nrem_fraction=0.7)
    r = m2.run(rec, seed=0, params=m2.M2Params(n_shuffles=10))
    assert not r.eligible and "PRE NREM frames" in r.reason and math.isnan(r.score)
    assert r.missing == ("PRE NREM frames >= 300",)


def test_result_has_caveat_and_is_deterministic():
    rec = scenario("positive", seed=1, tau_s=1.0)
    a = m2.run(rec, seed=0, params=m2.M2Params(n_shuffles=20))
    b = m2.run(rec, seed=0, params=m2.M2Params(n_shuffles=20))
    assert a.to_json() == b.to_json()
    assert "two pseudo-sessions" in a.details["caveat"]
    assert 1 / 21 <= a.p_n1 <= 1


def test_verdict_needs_both_splits():
    def res(sid, score, p, eligible=True):
        from toolbox.contract import MethodResult
        return MethodResult("M2", sid, eligible, "" if eligible else "x", score, p, 500, 0, {}, {})

    assert m2.verdict([res("A", 0.1, 0.01), res("B", 0.2, 0.002)])["answer"] == "yes"
    assert m2.verdict([res("A", 0.1, 0.01), res("B", 0.2, 0.2)])["answer"] == "no"
    assert m2.verdict([res("A", 0.1, 0.01), res("B", -0.2, 0.002)])["answer"] == "no"
    assert m2.verdict([res("A", 0.1, 0.01)])["answer"] == "not eligible"
    v = m2.verdict([res("A", 0.1, 0.01), res("B", float("nan"), float("nan"), eligible=False)])
    assert v["answer"] == "not eligible" and "two pseudo-sessions" in v["caveat"]


_CACHE = {}


def _yes_count(name, scale, require_blockswap):
    key = (name, scale)
    if key not in _CACHE:
        _CACHE[key] = [m2.run(scenario(name, seed=s, tau_s=1.0), seed=s,
                              params=m2.M2Params(n_shuffles=N_SHUFFLES_COUNTED)) for s in range(n_seeds(scale))]
    return sum(m2.is_yes(r, require_blockswap=require_blockswap) for r in _CACHE[key])


@pytest.mark.parametrize("bs", [False, pytest.param(True, marks=pytest.mark.xfail(
    strict=True, reason="block-swap null costs power: 8/10 at seeds 0-9 (seeds 0 and 6 p_blockswap > 0.1)"))],
    ids=["n1", "n1+blockswap"])
def test_m2_positive_control(scale, bs):
    k = _yes_count("positive", scale, bs)
    report(f"T-M2-1 positive ({'n1+bs' if bs else 'n1'})", scale, k, n_seeds(scale), ">= at_least")
    assert k >= at_least(scale, 45)


NEGATIVE = ["no_sleep_coactivity", "noise_only", "reversed",
            pytest.param("pre_existing", marks=pytest.mark.xfail(
                strict=True, reason="N1 alone: TASK patterns already in PRE give D2 > 0 by chance against a "
                                    "null near 0 (6/10 at seeds 0-9); see the n1+blockswap variant"))]


@pytest.mark.parametrize("name", NEGATIVE)
def test_m2_negative_controls_n1(name, scale):
    k = _yes_count(name, scale, False)
    report(f"T-M2 negative {name} (n1)", scale, k, n_seeds(scale), "<= at_most")
    assert k <= at_most(scale, 5)


@pytest.mark.parametrize("name", ["no_sleep_coactivity", "noise_only", "reversed", "pre_existing"])
def test_m2_negative_controls_blockswap(name, scale):
    k = _yes_count(name, scale, True)
    report(f"T-M2 negative {name} (n1+bs)", scale, k, n_seeds(scale), "<= at_most")
    assert k <= at_most(scale, 5)


def test_m2_reversed_sign():
    r = m2.run(scenario("reversed", seed=0, tau_s=1.0), seed=0, params=m2.M2Params(n_shuffles=20))
    assert r.score < 0
