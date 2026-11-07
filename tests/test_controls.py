"""Smoke test for run_controls (plan section 6); not a counted test."""

from reactivation.assemblies import AssemblyParams
from reactivation.controls import run_controls, scenario


def test_run_controls_smoke():
    like = scenario("positive", seed=0, tau_s=1.0)
    rep = run_controls("M3", like, seed=0, n_seeds=2, params=AssemblyParams(n_shuffles=50))
    assert rep.method_id == "M3" and rep.n_seeds == 2
    assert set(rep.fpr) == {"no_sleep_coactivity", "pre_existing", "other_assemblies"}
    assert 0.0 <= rep.tpr <= 1.0 and isinstance(rep.passed, bool)
    assert 0.7 < rep.matched["median_lag1"] < 1.0
