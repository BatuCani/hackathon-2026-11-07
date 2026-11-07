"""Shared helpers for counted tests (plans/engineer-b.md section 5).

Counted tests run twice: "fast" (10 seeds; "at least" -> 9/10, "at most" -> 2/10)
and "slow" (50 seeds, plan thresholds; run with `pytest -m slow`).
Both use 200 shuffles. Thresholds are [PROPOSAL]s copied from the plan, not tuned.
"""

import pytest

N_SHUFFLES_COUNTED = 200


@pytest.fixture(params=["fast", pytest.param("slow", marks=pytest.mark.slow)])
def scale(request):
    return request.param


def n_seeds(scale: str) -> int:
    return 10 if scale == "fast" else 50


def at_least(scale: str, slow_threshold: int) -> int:
    """Plan threshold "at least X/50"; fast run uses "at least 9/10"."""
    return 9 if scale == "fast" else slow_threshold


def at_most(scale: str, slow_threshold: int) -> int:
    """Plan threshold "at most X/50"; fast run uses "at most 2/10"."""
    return 2 if scale == "fast" else slow_threshold


def report(test_id: str, scale: str, count: int, total: int, rule: str) -> None:
    print(f"[{test_id}] {scale}: {count}/{total} ({rule})")
