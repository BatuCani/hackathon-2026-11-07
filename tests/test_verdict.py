"""Tests for the verdict rule and summary generation (task T7 in TASKS.md).

Tests cover:
1. Reactivation likely (at least two counted methods say yes in both splits,
   and no counted method says yes in reversed direction).
2. Reactivation not supported (no counted method says yes in either split).
3. Not enough evidence (disagreement across splits, fewer than two counted methods,
   or reversed direction veto).
4. Ineligible methods (listed with missing data, not counted).
5. Failed control methods (failed method tests, not counted).
6. Summary markdown generation for results/real/summary.md.
"""

from pathlib import Path
import pytest

from toolbox.contract import MethodResult
from toolbox.controls import ControlReport
from toolbox.verdict import (
    VerdictResult,
    compute_verdict,
    generate_summary_markdown,
    method_says_yes,
)


def make_result(
    method_id: str,
    session_id: str,
    *,
    eligible: bool = True,
    reason: str = "",
    score: float = 0.1,
    p_n1: float = 0.01,
    n_shuffles: int = 500,
    seed: int = 0,
    missing: tuple[str, ...] = (),
    details: dict | None = None,
) -> MethodResult:
    return MethodResult(
        method_id=method_id,
        session_id=session_id,
        eligible=eligible,
        reason=reason,
        score=score if eligible else float("nan"),
        p_n1=p_n1 if eligible else float("nan"),
        n_shuffles=n_shuffles,
        seed=seed,
        params={},
        details=details or {},
        missing=missing,
    )


def test_method_says_yes_threshold():
    # Yes: eligible, score > 0, p_n1 < 0.05
    yes_res = make_result("M1", "split_a", score=0.05, p_n1=0.049)
    assert method_says_yes(yes_res) is True

    # No: score <= 0
    zero_score = make_result("M1", "split_a", score=0.0, p_n1=0.01)
    assert method_says_yes(zero_score) is False
    neg_score = make_result("M1", "split_a", score=-0.1, p_n1=0.01)
    assert method_says_yes(neg_score) is False

    # No: p_n1 >= 0.05
    high_p = make_result("M1", "split_a", score=0.2, p_n1=0.05)
    assert method_says_yes(high_p) is False

    # No: ineligible
    ineligible = make_result("M1", "split_a", eligible=False, score=0.5, p_n1=0.001)
    assert method_says_yes(ineligible) is False


def test_verdict_reactivation_likely():
    # Two methods (M1, M3) say yes in both split_a and split_b
    results = [
        make_result("M1", "split_a", score=0.15, p_n1=0.01),
        make_result("M1", "split_b", score=0.12, p_n1=0.02),
        make_result("M3", "split_a", score=0.08, p_n1=0.005),
        make_result("M3", "split_b", score=0.09, p_n1=0.01),
    ]
    controls = {"M1": True, "M3": True}

    verdict = compute_verdict(results, controls=controls)
    assert verdict.verdict == "Reactivation likely"
    assert verdict.counted_methods == ["M1", "M3"]
    assert verdict.how_likely["split_a"] == 1.0
    assert verdict.how_likely["split_b"] == 1.0
    assert verdict.how_likely_str["split_a"] == "2/2"
    assert verdict.how_likely_str["split_b"] == "2/2"
    assert verdict.yes_both_splits == ["M1", "M3"]
    assert len(verdict.reversed_yes_methods) == 0


def test_verdict_reactivation_not_supported():
    # Two counted methods (M1, M3), but neither says yes in either split
    results = [
        make_result("M1", "split_a", score=-0.05, p_n1=0.8),
        make_result("M1", "split_b", score=-0.02, p_n1=0.6),
        make_result("M3", "split_a", score=0.01, p_n1=0.25),
        make_result("M3", "split_b", score=-0.10, p_n1=0.9),
    ]
    controls = {"M1": True, "M3": True}

    verdict = compute_verdict(results, controls=controls)
    assert verdict.verdict == "Reactivation not supported"
    assert verdict.counted_methods == ["M1", "M3"]
    assert verdict.how_likely["split_a"] == 0.0
    assert verdict.how_likely["split_b"] == 0.0
    assert verdict.how_likely_str["split_a"] == "0/2"
    assert verdict.how_likely_str["split_b"] == "0/2"
    assert len(verdict.yes_both_splits) == 0


def test_verdict_not_enough_evidence_disagreement():
    # M1 says yes in both splits, but M3 says yes in split_a and no in split_b
    results = [
        make_result("M1", "split_a", score=0.15, p_n1=0.01),
        make_result("M1", "split_b", score=0.12, p_n1=0.02),
        make_result("M3", "split_a", score=0.08, p_n1=0.01),
        make_result("M3", "split_b", score=-0.05, p_n1=0.4),
    ]
    controls = {"M1": True, "M3": True}

    verdict = compute_verdict(results, controls=controls)
    assert verdict.verdict == "Not enough evidence"
    assert verdict.counted_methods == ["M1", "M3"]
    assert verdict.how_likely_str["split_a"] == "2/2"
    assert verdict.how_likely_str["split_b"] == "1/2"
    assert verdict.yes_both_splits == ["M1"]


def test_verdict_not_enough_evidence_ineligible_methods():
    # M1 is eligible and says yes in both splits.
    # M3 and M4 are ineligible, so only M1 is counted (< 2 counted methods).
    results = [
        make_result("M1", "split_a", score=0.2, p_n1=0.01),
        make_result("M1", "split_b", score=0.2, p_n1=0.01),
        make_result(
            "M3", "split_a", eligible=False,
            reason="0 TASK components above N1 bound",
            missing=("at least 1 TASK component above N1 bound",),
        ),
        make_result(
            "M3", "split_b", eligible=False,
            reason="0 TASK components above N1 bound",
            missing=("at least 1 TASK component above N1 bound",),
        ),
    ]
    controls = {"M1": True, "M3": True}

    verdict = compute_verdict(results, controls=controls)
    assert verdict.verdict == "Not enough evidence"
    assert verdict.counted_methods == ["M1"]
    assert "M3" in verdict.ineligible_methods
    assert verdict.how_likely_str["split_a"] == "1/1"
    assert verdict.how_likely_str["split_b"] == "1/1"


def test_verdict_not_enough_evidence_failed_controls():
    # M1 and M3 both say yes in both splits, but M3 failed method tests.
    results = [
        make_result("M1", "split_a", score=0.15, p_n1=0.01),
        make_result("M1", "split_b", score=0.12, p_n1=0.02),
        make_result("M3", "split_a", score=0.10, p_n1=0.01),
        make_result("M3", "split_b", score=0.10, p_n1=0.01),
    ]
    # M3 failed control
    report_m3 = ControlReport(
        method_id="M3", tpr=0.7, fpr={"no_sleep_coactivity": 0.2},
        passed=False, thresholds={"min_tpr": 0.9, "max_fpr": 0.1},
    )
    controls = {"M1": True, "M3": report_m3}

    verdict = compute_verdict(results, controls=controls)
    assert verdict.verdict == "Not enough evidence"
    assert verdict.counted_methods == ["M1"]
    assert verdict.failed_control_methods == ["M3"]
    assert verdict.how_likely_str["split_a"] == "1/1"
    assert verdict.how_likely_str["split_b"] == "1/1"


def test_verdict_reversed_direction_veto():
    # M1 and M3 say yes in both splits in forward direction.
    # But M1 says yes in the reversed direction.
    results = [
        make_result("M1", "split_a", score=0.15, p_n1=0.01),
        make_result("M1", "split_b", score=0.12, p_n1=0.02),
        make_result("M3", "split_a", score=0.08, p_n1=0.005),
        make_result("M3", "split_b", score=0.09, p_n1=0.01),
    ]
    reversed_results = [
        make_result("M1", "split_a", score=0.05, p_n1=0.02),  # reversed says yes!
        make_result("M3", "split_a", score=-0.1, p_n1=0.8),
    ]
    controls = {"M1": True, "M3": True}

    verdict = compute_verdict(results, controls=controls, reversed_results=reversed_results)
    assert verdict.verdict == "Not enough evidence"
    assert "M1" in verdict.reversed_yes_methods


def test_verdict_zero_counted_methods():
    results = [
        make_result("M1", "split_a", eligible=False, reason="Too few cells"),
        make_result("M1", "split_b", eligible=False, reason="Too few cells"),
    ]
    verdict = compute_verdict(results, controls={"M1": True})
    assert verdict.verdict == "Not enough evidence"
    assert verdict.counted_methods == []
    assert verdict.how_likely["split_a"] == 0.0
    assert verdict.how_likely_str["split_a"] == "0/0"


def test_generate_summary_markdown(tmp_path: Path):
    results = [
        make_result("M1", "split_a", score=0.15, p_n1=0.01),
        make_result("M1", "split_b", score=0.12, p_n1=0.02),
        make_result("M3", "split_a", score=0.08, p_n1=0.005),
        make_result("M3", "split_b", score=0.09, p_n1=0.01),
        make_result("M4", "split_a", eligible=False, reason="TASK frames < 5x cells", missing=("TASK frames >= 5x cells",)),
        make_result("M4", "split_b", eligible=False, reason="TASK frames < 5x cells", missing=("TASK frames >= 5x cells",)),
    ]
    controls = {
        "M1": True,
        "M3": True,
        "M4": ControlReport("M4", tpr=0.8, fpr={}, passed=False, thresholds={}),
    }
    reversed_results = [
        make_result("M1", "split_a", score=-0.1, p_n1=0.9),
        make_result("M3", "split_a", score=-0.05, p_n1=0.8),
    ]

    verdict = compute_verdict(results, controls=controls, reversed_results=reversed_results)
    out_file = tmp_path / "summary.md"
    md = generate_summary_markdown(
        verdict=verdict,
        results=results,
        controls=controls,
        reversed_results=reversed_results,
        out_path=out_file,
    )

    assert out_file.is_file()
    assert "Reactivation likely" in md
    assert "M1" in md
    assert "M3" in md
    assert "M4" in md
    assert "TASK frames < 5x cells" in md
    assert "split_a" in md
    assert "split_b" in md
