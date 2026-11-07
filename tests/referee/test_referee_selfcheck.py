"""The referee itself: it must fail deliberately wrong methods, and its README must match its numbers.

The straw men below are wrong on purpose; they are not the team's methods.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import numpy as np
import pytest

from referee import rules

cases = pytest.importorskip("referee.cases", reason="needs toolbox.synth (Engineer B, eng-b/toolbox)")
from toolbox.contract import MethodResult, analysis_mask

N = rules.N_SHUFFLES


def _result(name, rec, score, p, eligible=True):
    return MethodResult(
        method_id=name, session_id=rec.session_id, eligible=eligible, reason="",
        score=float(score), p_n1=float(p), n_shuffles=N, seed=0, params={}, details={},
    )


def always_yes(rec, seed):
    return _result("always_yes", rec, 1.0, 1 / (1 + N))


def always_no(rec, seed):
    return _result("always_no", rec, np.nan, np.nan, eligible=False)


def rate_up(rec, seed):
    """Wrong: "TASK-active cells are more active in POST than PRE" (the rate confound)."""
    rng = np.random.default_rng(seed)
    task = rec.deconv[:, analysis_mask(rec, "TASK")].mean(axis=1)
    top = np.argsort(task)[-len(task) // 4 :]
    pre = rec.deconv[top][:, analysis_mask(rec, "PRE")].mean(axis=0)
    post = rec.deconv[top][:, analysis_mask(rec, "POST")].mean(axis=0)
    both, n_post = np.concatenate([pre, post]), post.size
    score = post.mean() - pre.mean()
    null = np.empty(N)
    for i in range(N):
        perm = rng.permutation(both)
        null[i] = perm[:n_post].mean() - perm[n_post:].mean()
    return _result("rate_up", rec, score, (1 + np.sum(null >= score)) / (1 + N))


def _upper(Z):
    C = np.corrcoef(Z)
    return np.nan_to_num(C[np.triu_indices(C.shape[0], 1)])


def ignores_pre(rec, seed):
    """Wrong: "POST resembles TASK", with no PRE baseline; N1 on POST."""
    rng = np.random.default_rng(seed)
    t = _upper(rec.deconv[:, analysis_mask(rec, "TASK")])
    post = rec.deconv[:, analysis_mask(rec, "POST")]
    score = np.corrcoef(t, _upper(post))[0, 1]
    B = post.shape[1]
    null = np.empty(N)
    for i in range(N):
        off = rng.integers(1, B, post.shape[0])
        idx = (np.arange(B)[None, :] - off[:, None]) % B
        null[i] = np.corrcoef(t, _upper(np.take_along_axis(post, idx, axis=1)))[0, 1]
    return _result("ignores_pre", rec, score, (1 + np.sum(null >= score)) / (1 + N))


def _judge(method, case):
    verdicts = [rules.says_yes(method(cases.make_case(case, s), s)) for s in rules.SEEDS]
    return rules.judge(case, cases.EXPECTED_YES[case], verdicts)


@pytest.mark.parametrize(
    "method, must_fail, must_pass",
    [
        (always_yes, ("b_noise", "c_preexisting", "d_rate_only"), ("a_reactivation",)),
        (always_no, ("a_reactivation",), ("b_noise", "c_preexisting", "d_rate_only")),
        (rate_up, ("d_rate_only",), ("a_reactivation",)),
        (ignores_pre, ("c_preexisting",), ("a_reactivation",)),
    ],
    ids=["always_yes", "always_no", "rate_up", "ignores_pre"],
)
def test_referee_fails_wrong_methods(method, must_fail, must_pass):
    for case in must_fail:
        j = _judge(method, case)
        assert not j.passed, f"referee let {method.__name__} pass {case}: yes {j.n_yes}/{j.n}"
    for case in must_pass:
        j = _judge(method, case)
        assert j.passed, f"{method.__name__} should pass {case} (it is caught elsewhere): yes {j.n_yes}/{j.n}"


def test_says_yes_rejects_malformed_results():
    rec = cases.make_case("b_noise", rules.SEEDS[0])
    with pytest.raises(AssertionError, match="n_shuffles"):
        rules.says_yes(dataclasses.replace(_result("x", rec, 1.0, 0.01), n_shuffles=200))
    with pytest.raises(AssertionError, match="non-finite"):
        rules.says_yes(_result("x", rec, np.nan, 0.01))
    with pytest.raises(AssertionError, match="outside"):
        rules.says_yes(_result("x", rec, 1.0, 0.0))
    blocked = dataclasses.replace(_result("x", rec, 1.0, 0.01), details={"p_blockswap": 0.2})
    assert not rules.says_yes(blocked)
    assert rules.says_yes(_result("x", rec, 1.0, 0.01))
    assert not rules.says_yes(_result("x", rec, -1.0, 0.01))


def test_readme_matches_rules():
    readme = (Path(__file__).parent / "README.md").read_text()
    expected = {
        "ALPHA": rules.ALPHA,
        "N_SHUFFLES": rules.N_SHUFFLES,
        "SEEDS": ", ".join(map(str, rules.SEEDS)),
        "POS_MIN_YES": rules.POS_MIN_YES,
        "NEG_MAX_YES": rules.NEG_MAX_YES,
        "TIME_BUDGET_S": int(rules.TIME_BUDGET_S),
        "N_CELLS": cases.N_CELLS,
        "FS": cases.FS,
        "TAU_S": cases.TAU_S,
        "P_TASK": cases.P_TASK,
        "P_SLEEP": cases.P_SLEEP,
        "EXTRA_RATE_HZ": cases.EXTRA_RATE_HZ,
    }
    for name, value in expected.items():
        m = re.search(rf"^\| `{name}` \| ([^|]+) \|", readme, re.MULTILINE)
        assert m, f"README.md has no row for `{name}`"
        assert m.group(1).strip() == str(value), f"README `{name}` = {m.group(1).strip()}, rules = {value}"
