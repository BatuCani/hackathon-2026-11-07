# Engineer B journal (append-only)

Pen, no eraser: every step writes here, failures too (`research/research-loop.png`).
Labels: verified / contradicted / not enough evidence.
Plan: `plans/engineer-b.md`.

## Entry 0 - 2026-11-07 14:50 - Step 0 sync

Open questions of `plans/engineer-b.md` section 9 were not answered by A, Zixi or the scientist before work started.
Work proceeds on the plan's recommended defaults; each one stays a [TEAM DECISION] until confirmed.

| # | Question | Default used | Status |
|---|---|---|---|
| 1 | Method IDs | team-brief IDs (M3 PCA, M4 ICA) in code and results | unconfirmed |
| 2 | Bootstrap PR | B wrote `pyproject.toml`, `src/reactivation/contract.py` verbatim from plan section 2, because main had no code; A must review before merge | unconfirmed |
| 3 | Dataset, fs, cells, frames | unknown; loader not on main; B runs on synthetic sessions only | open |
| 4 | `session_type` per session or segment | per session (metadata only for B) | unconfirmed |
| 5 | TASK frames | all non-`unscored` TASK frames | unconfirmed |
| 6 | Score aggregation, alpha | mean of per-component deltas; alpha 0.05 | unconfirmed |
| 7 | N1 details | shift the NREM-only concatenated analysis matrix; offsets on [1, B-1]; bound = 95th percentile of per-shuffle max eigenvalue | unconfirmed |
| 8 | `p_blockswap` | computed and reported next to `p_n1` (20 s blocks, 500 reassignments) | unconfirmed |
| 9 | Minima | 10 cells, B_task >= 5 N, 300 NREM frames per sleep epoch, zero-variance cells dropped from all epochs | unconfirmed |
| 10 | Cut-off "Needs" cells | read as "at least one significant TASK component" (M3), "at least two significant components" (M4) | unconfirmed |
| 11 | Who locks test thresholds | not locked by the scientist; plan section 5 thresholds are used as written and are not changed after results | open |
| 12 | Journal layout | one journal per engineer under `journal/` | unconfirmed |

Python: plan says 3.12 with `uv`; `pyproject.toml` pins `>=3.12`, run with `uv run --python 3.12`.

## Entry 1 - 2026-11-07 15:00 - Steps 1-4, tests written before implementation

READ: `plans/engineer-b.md` section 5 (test table), section 4 Steps 1-4 (math); `research/source-of-truth.md` "Shared preprocessing", M4, M5, M6; `research/team-brief.md` section 4.
Quote (team brief section 4): "shift each neuron's trace by its own random circular offset, 500 times; keeps each neuron's autocorrelation, breaks co-activity."

Tests written first, all thresholds copied from plan section 5 ([PROPOSAL], not locked by the scientist, not to be changed after results):
`tests/test_synth.py` (T-S1..3), `tests/test_n1.py` (T-N1-1..9), `tests/test_assemblies.py` (T-A1..5), `tests/test_m3.py` (T-M3-1..8), `tests/test_m4.py` (T-M4-1..4).
Choices made while writing tests (not in the plan; flagged):
- T-S3 uses the median lag-1 autocorrelation across cells.
- M3/M4 controls use tau_s = 1 in every scenario (the plan fixes tau_s = 1 only for T-M3-1 and T-M3-5); this is the harder case.
- T-M4-1 uses two assemblies of 8 cells sharing 4 cells, seed 0, ground truth = normalised membership vectors.
- Fast run: 10 seeds, 200 shuffles; slow (counted) run: 50 seeds, 200 shuffles (`pytest -m slow`).

PREDICT (before any run; from the plan's planning pre-check, which is not a finding):
- T-N1-7: N1 bound about 1.19-1.21 for N=50, B=6000, independent bins.
- T-N1-8: N1 gives >= 1 false component in about 1/20 seeds; MP gives about 11-14 false components per seed.
- T-N1-9: 3 components recovered in nearly every seed.
- T-M3-1: positive control detected in nearly every seed.
- T-M3-2: about 2/40 false positives; T-M3-3: p_n1 anticonservative (about 7/40), p_blockswap about 3/40.
- T-M4-1: ICA separates overlapping assemblies (|cos| >= 0.9) where PCA mixes them (about 0.68 by the sum/difference argument).

## Entry 2 - 2026-11-07 15:05 - fast run (10 seeds, 200 shuffles)

RUN: `uv run --python 3.12 pytest -q` at commit 1745e34, seeds 0-9.
JUDGE: 32 tests passed; 1 failed: T-M4-1.
- T-M4-1 (seed 0, locked threshold): ICA matched |cos| 0.911 (>= 0.9, pass), PCA 0.817 (< 0.8 required, fail).
  Diagnostic sweep, seeds 0-9 (not a counted test, threshold unchanged): ICA >= 0.9 in 5/10 seeds; PCA < 0.8 in 9/10; ICA > PCA in 9/10.
  In seeds 1 and 5 ICA stays near the PCA mix (0.68, 0.70).
  Prediction "ICA |cos| >= 0.9, PCA about 0.68" is partly contradicted: PCA is often above the sum/difference value (0.68-0.82) and ICA misses 0.9 in half the seeds.
  RECORD label: **contradicted** (T-M4-1 as written). Not fixed by changing the threshold. Possible causes, untested: FastICA local optimum in 2 dimensions; unequal activation counts rotate the PCs toward single assemblies.
- Fast-run counts (from pytest -s output): T-M3-3 p_n1 2/10 (info), T-M4-2 no_sleep_coactivity 1/10, pre_existing p_blockswap 1/10, other_assemblies 2/10, noise_only ineligible 10/10; T-N1-8 MP >= 5 false components 10/10.
RECORD: fast run is a smoke check only; counted run (50 seeds) in Entry 3.

READ: `research/datasets/calcium-vetting.md` (main, f86fcbc, by Batu). Quote: "TASK = frames 5481-7306 (239 s wake), PRE = 1,300 NREM frames (170 s), POST = 999 NREM frames (131 s)", RIKEN session "6,920 cells x 19,000 frames".
Consequence for B (needs a TEAM DECISION, not decided here): with N = 6920 cells and B_task = 1825 (split A) or 650 (split B), the minimum B_task >= 5 N fails, so M3 and M4 report `eligible=False` with that reason.
N > B_task also makes the TASK correlation matrix rank-deficient. Options for the team: restrict to the most active cells so that N <= B_task / 5 (about 365 cells for split A), or lower the minimum. Cost: one N1 shuffle at N = 6920 is about N^2 B = 8.7e10 flops; 500 shuffles will not fit before 17:00 without cell selection.

## Entry 3 - 2026-11-07 15:15 - counted run (50 seeds, 200 shuffles) and run_b.py

Correction to Entry 2: its time stamp "15:05" was written early; the fast run finished at about 15:00.

RUN: `uv run --python 3.12 pytest -m slow -s` at commit 1745e34; 10 passed, 0 failed, 910 s.
JUDGE (locked plan thresholds), RECORD label in brackets:

| Test | Result | Threshold | Label |
|---|---|---|---|
| T-N1-8 N1 >= 1 false component | 2/50 | at most 5/50 | verified |
| T-N1-8 MP >= 5 false components | 50/50 | at least 45/50 | verified |
| T-N1-9 planted recovery, tau 0 | 50/50 | at least 47/50 | verified |
| T-N1-9 planted recovery, tau 1 | 48/50 | at least 47/50 | verified |
| T-M3-1 positive | 50/50 | at least 47/50 | verified |
| T-M3-2 no sleep co-activity | 1/50 | at most 5/50 | verified |
| T-M3-3 pre-existing, p_blockswap | 3/50 | at most 5/50 | verified |
| T-M3-3 pre-existing, p_n1 (not gated) | 7/50 | reported | p_n1 alone is anticonservative here, as the plan predicted (7/40) |
| T-M3-4 other assemblies | 2/50 | at most 5/50 | verified |
| T-M3-5 noise only ineligible | 49/50 | at least 45/50 | verified |
| T-M3-8 reversal | 50/50 | at least 47/50 | verified |
| T-M4-2 (T-M3-1..5 for M4) | 50/50, 1/50, 3/50 (p_n1 7/50), 2/50, 50/50 | as M3 | verified |
| T-M4-1 overlap, seed 0 | ICA 0.911, PCA 0.817 | ICA >= 0.9, PCA < 0.8 | contradicted (Entry 2) |

Predictions in Entry 1 matched except T-M4-1.
The brief's claim "the analytical bound is too lenient for calcium" is verified on synthetic data: with tau_s = 1 and no assemblies, MP gives >= 5 false components in 50/50 seeds, N1 gives >= 1 in 2/50 (`tests/test_n1.py::test_t_n1_8`).

RUN: `uv run --python 3.12 python scripts/run_b.py --seed 0 --controls` (500 shuffles), loader not merged, so synthetic sessions only (`summary.csv` column `data`).
RECORD: `results/engineer-b/summary.csv`, `controls.json`, per-session JSON and R(t) `.npz`.
- control-positive-0: M3 score 0.156, p_n1 0.006, p_blockswap 0.056; M4 score 0.154, p_n1 0.006, p_blockswap 0.056. Under the "require both p < 0.05" rule this single session would be a "no": block-swap has low power with about 20 blocks per epoch. [not enough evidence, single seed]
- controls.json (20 matched seeds, rule score > 0 & p_n1 < 0.05 & p_blockswap < 0.05): M3 tpr 0.95, fpr 0.10 / 0.10 / 0.10; M4 tpr 0.95, fpr 0.05 / 0.10 / 0.10; both pass the [PROPOSAL] thresholds (tpr >= 0.9, fpr <= 0.1), at the edge.
- Diagnostic (not a test): with tau_s = 1 the per-seed PRE and POST mean strengths scatter by about +-0.1 with no planted sleep activity (seed 0: PRE 0.105, POST -0.066); tau_s = 0 stays within +-0.02. No systematic PRE/POST bias was found.

Not done: optional neurospatial cross-check (plan section 7). Installing neurospatial from GitHub was blocked by this machine's permission policy; it needs the user's approval.
