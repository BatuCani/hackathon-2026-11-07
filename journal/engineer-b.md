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
