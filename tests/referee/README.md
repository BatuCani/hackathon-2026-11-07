# Referee

**Status: PROPOSED - lock after the scientist signs.**
Until then every number below may change.
After signing, write the signing commit in the lock block at the end; from then on the referee is frozen, and any change is a new, dated referee version, never an edit.

The referee is the locked test that passes the right answer and fails a wrong one.
It runs every method (M1 to M4, team-brief IDs) on synthetic sessions whose truth is planted, and judges each method by one fixed rule.
It does not implement any method.

## Cases

Each case is a synthetic session from Engineer B's generator `toolbox.synth.make_session` (branch `eng-b/toolbox`, commit 33d3041), built in [cases.py](cases.py).
Three assemblies of 8 cells (cells 0 to 23) are planted in TASK; PRE and POST use NREM frames only.

| Case | Planted truth | Correct answer |
|---|---|---|
| `a_reactivation` | assemblies co-active in TASK and in POST, not in PRE | yes |
| `b_noise` | independent cells, no assembly in any epoch | no |
| `c_preexisting` | assemblies co-active in TASK, and equally in PRE and POST | no |
| `d_rate_only` | assemblies co-active in TASK only; in POST NREM the members get extra independent events, so their activity rises about 2.3x without any co-activity (the Tingley & Peyrache firing-rate confound) | no |

Case `d_rate_only` is the one the generator lacks; [cases.py](cases.py) adds it as a perturbation of a no-sleep-co-activity session, with the same AR(1) calcium filter.
[test_referee_cases.py](test_referee_cases.py) checks that each case carries its planted truth (member co-activity per epoch, member rate ratio), without calling any method.

## Decision rule

One session says **yes** when the method's `MethodResult` has `eligible`, `score > 0` and `p_n1 < ALPHA`, and also `details["p_blockswap"] < ALPHA` if the method reports `p_blockswap` ([rules.py](rules.py), `says_yes`).
An ineligible method says no.
An eligible result with a non-finite score or p, a p outside [1/501, 1], or `n_shuffles` other than 500 is a malformed result and fails the test.

Per method and case, the referee runs one session per seed and counts the yes answers:

- case `a_reactivation` passes with at least `POS_MIN_YES` yes out of 5;
- cases `b_noise`, `c_preexisting`, `d_rate_only` pass with at most `NEG_MAX_YES` yes out of 5.

A method passes the referee when it passes all four cases.
Why these counts: a calibrated method says yes in a null case with probability 0.05, so 3 or more yes out of 5 happens with probability 0.0012 per case (about 1 percent over the 12 negative cells); a method that ignores PRE, or reads a rate change as reactivation, says yes in 5 of 5.

## Numbers (PROPOSED)

| Name | Value | Meaning |
|---|---|---|
| `ALPHA` | 0.05 | one-sided level for yes, as in PROBLEM.md |
| `N_SHUFFLES` | 500 | N1 shuffles every eligible result must report (team brief section 4) |
| `SEEDS` | 0, 1, 2, 3, 4 | one session per seed and case; the method gets the same seed |
| `POS_MIN_YES` | 4 | minimum yes out of 5 in `a_reactivation` |
| `NEG_MAX_YES` | 2 | maximum yes out of 5 in each negative case |
| `TIME_BUDGET_S` | 30 | whole referee, one core; exceeding it fails the run |
| `N_CELLS` | 40 | cells per session |
| `FS` | 7.65 | frame rate in Hz, as the RIKEN data |
| `TAU_S` | 0.11 | AR(1) time constant in s; lag-1 autocorrelation 0.30, the 75th percentile of RIKEN `spike` (segment 0, median 0.17) |
| `P_TASK` | 0.03 | assembly activation probability per TASK frame |
| `P_SLEEP` | 0.02 | assembly activation probability per NREM frame, where the case plants it |
| `EXTRA_RATE_HZ` | 1.0 | case d: extra independent event rate per member in POST NREM |

Session shape: PRE 800, TASK 600, POST 800 frames, NREM fraction 0.7, so 560 NREM frames in PRE and in POST (minimum 300 per the plan's requirement check).
[test_referee_selfcheck.py](test_referee_selfcheck.py) fails if this table and the code disagree.

## The referee checks itself

[test_referee_selfcheck.py](test_referee_selfcheck.py) runs four deliberately wrong straw-man methods and requires the referee to fail each one:

| Straw man | Wrong because | Must fail |
|---|---|---|
| `always_yes` | answers yes regardless | `b_noise`, `c_preexisting`, `d_rate_only` |
| `always_no` | answers no regardless | `a_reactivation` |
| `rate_up` | TASK-active cells more active in POST than PRE | `d_rate_only` |
| `ignores_pre` | POST resembles TASK, no PRE baseline | `c_preexisting` |

## Status of the methods

- M3 and M4 (Engineer B, `toolbox/m3_pca.py`, `toolbox/m4_ica.py`) run against the referee now.
- M1 and M2 are xfail until `toolbox.m1_pair_corr.run` and `toolbox.m2_ev_rev.run` exist (today the modules hold docstrings only) with the interface `run(rec, *, seed, params=None) -> MethodResult` (plans/engineer-b.md section 2.2); the moment they exist, the tests count.
- M2 is defined across sessions (EV > REV across sessions); the referee calls it per session and reads `score` as EV - REV and `p_n1` against N1, as the PROBLEM.md key D2 does per split.

## Pre-check before proposing (not a finding)

Run once on 2026-11-07 to check that the numbers are reachable, before any real-data result.

- Engineer B's M3 and M4 (commit 33d3041): yes in 5/5 of `a_reactivation` and 0/5 of each negative case; the same with `p_n1` alone, without `p_blockswap`.
- A throwaway reference M1 (key D1) and M2 (key D2) with N1, kept outside the repository: M1 5/5, 0/5, 0/5, 0/5; M2 5/5, 0/5, 2/5, 0/5 (cases a, b, c, d), so M2 sits at the limit in `c_preexisting`.
- All four methods together: 21.8 s of the 30 s budget, one core.

## Run

```sh
uv run pytest tests/referee -q -rx -s
```

`-s` prints one `[referee]` line per method and case with the yes count, and the total time against the budget.

## Lock

- Signed by (scientist):
- Date and time:
- Referee commit at signing:
