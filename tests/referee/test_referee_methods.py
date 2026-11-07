"""The referee: every method on every case, judged by `rules.says_yes` and `rules.judge`.

A method that does not exist yet is xfail; once its module defines `run`, the test counts.
"""

from __future__ import annotations

import importlib

import pytest

from referee import rules


def _import_or_xfail(name: str):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        if e.name and (name == e.name or name.startswith(e.name + ".")):
            pytest.xfail(f"{name} not implemented yet")
        raise


def _run_or_xfail(method_id: str):
    module = _import_or_xfail(rules.METHODS[method_id])
    run = getattr(module, "run", None)
    if run is None:
        pytest.xfail(f"{rules.METHODS[method_id]}.run not implemented yet")
    return run


@pytest.mark.parametrize("case", ["a_reactivation", "b_noise", "c_preexisting", "d_rate_only"])
@pytest.mark.parametrize("method_id", list(rules.METHODS))
def test_referee(method_id: str, case: str):
    cases = _import_or_xfail("referee.cases")
    run = _run_or_xfail(method_id)
    verdicts, lines = [], []
    for seed in rules.SEEDS:
        try:
            r = run(cases.make_case(case, seed), seed=seed)
        except NotImplementedError:
            pytest.xfail(f"{method_id}.run raises NotImplementedError")
        assert r.method_id == method_id, r.method_id
        yes = rules.says_yes(r)
        verdicts.append(yes)
        lines.append(
            f"seed {seed}: eligible={r.eligible} score={r.score:.4g} p_n1={r.p_n1:.4g} "
            f"p_blockswap={(r.details or {}).get('p_blockswap')} yes={yes} {r.reason}"
        )
    j = rules.judge(case, cases.EXPECTED_YES[case], verdicts)
    print(f"[referee] {method_id} {case}: yes {j.n_yes}/{j.n}, rule {j.rule}, passed={j.passed}")
    assert j.passed, f"{method_id} on {case}: yes {j.n_yes}/{j.n}, needs {j.rule}\n" + "\n".join(lines)
