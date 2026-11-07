"""The referee's numbers and its one decision rule. PROPOSED - lock after the scientist signs.

Every value here is mirrored in tests/referee/README.md;
test_referee_selfcheck.py fails if the two disagree.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

ALPHA = 0.05  # one-sided significance level for "yes"
N_SHUFFLES = 500  # N1 shuffles every method must report [research/team-brief.md section 4]
SEEDS: tuple[int, ...] = (0, 1, 2, 3, 4)  # one synthetic session per seed and case
POS_MIN_YES = 4  # case a passes if at least this many of the 5 sessions say yes
NEG_MAX_YES = 2  # cases b, c, d pass if at most this many of the 5 sessions say yes
TIME_BUDGET_S = 30.0  # whole referee, one core

# Method modules and their entry point, per plans/engineer-b.md sections 2.2 and 3.
# Each module exposes run(rec, *, seed, params=None) -> MethodResult.
METHODS: dict[str, str] = {
    "M1": "toolbox.m1_pair_corr",
    "M2": "toolbox.m2_ev_rev",
    "M3": "toolbox.m3_pca",
    "M4": "toolbox.m4_ica",
}


def says_yes(result) -> bool:
    """A method result says "reactivation yes".

    yes = eligible and score > 0 and p_n1 < ALPHA,
    and also details["p_blockswap"] < ALPHA when the method reports it
    (plans/engineer-b.md Step 3 proposes it for the pre-existing-assembly case).
    An ineligible method says no.
    """
    if not result.eligible:
        return False
    score, p = float(result.score), float(result.p_n1)
    if not (math.isfinite(score) and math.isfinite(p)):
        raise AssertionError(f"eligible result with non-finite score={score} or p_n1={p}")
    if not 1.0 / (1 + N_SHUFFLES) - 1e-12 <= p <= 1.0:
        raise AssertionError(f"p_n1={p} outside [1/{1 + N_SHUFFLES}, 1]")
    if result.n_shuffles != N_SHUFFLES:
        raise AssertionError(f"n_shuffles={result.n_shuffles}, the brief requires {N_SHUFFLES}")
    yes = score > 0 and p < ALPHA
    p_block = (result.details or {}).get("p_blockswap")
    if p_block is not None:
        yes = yes and float(p_block) < ALPHA
    return yes


@dataclass(frozen=True)
class Judgement:
    case: str
    expected_yes: bool
    n_yes: int
    n: int
    passed: bool
    rule: str


def judge(case: str, expected_yes: bool, verdicts: Sequence[bool]) -> Judgement:
    """Turn one method's per-seed yes/no on one case into pass / fail."""
    n_yes, n = sum(bool(v) for v in verdicts), len(verdicts)
    if expected_yes:
        passed, rule = n_yes >= POS_MIN_YES, f"yes in >= {POS_MIN_YES}/{len(SEEDS)}"
    else:
        passed, rule = n_yes <= NEG_MAX_YES, f"yes in <= {NEG_MAX_YES}/{len(SEEDS)}"
    if n != len(SEEDS):
        raise AssertionError(f"judged {n} sessions, the referee uses {len(SEEDS)}")
    return Judgement(case, expected_yes, n_yes, n, passed, rule)
