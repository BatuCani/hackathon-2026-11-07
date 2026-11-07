# Reactivation toolbox

Claude Impact Lab hackathon project, 2026-11-07.
Submission text: [SUBMISSION.md](SUBMISSION.md); demo script: [DEMO.md](DEMO.md).

An open toolbox that asks whether neurons recorded with two-photon calcium imaging show sleep reactivation: sleep after a task (POST) resembling the task (TASK) more than sleep before it (PRE), NREM frames only.
It runs four standard methods (Tingley and Peyrache 2020: M1 cell-pair correlation, M2 explained variance vs. reverse, M3 PCA and M4 ICA reactivation strength), each against the same null (N1: every neuron's trace circularly shifted by its own random offset, 500 times, seed 0).
The question, number, unit and "yes" threshold per method are fixed in [PROBLEM.md](PROBLEM.md), and a method only counts if it passes planted-truth synthetic controls ([tests/referee/](tests/referee/)).
On the one public RIKEN calcium session the answer is **not enough evidence**, and no counted method says "yes"; on 8 rat electrophysiology sessions with known reactivation (DANDI:000044, used only as a positive control) M3 says "yes" in 8/8, so the toolbox can say "yes" on real data.

## Key findings

| Finding | Numbers | Files |
|---|---|---|
| RIKEN mouse05, overall verdict | not enough evidence: only M1 is counted in both splits, the rule needs two; hand-applied, `verdict.py` not yet wired into `run.py` | [SUBMISSION.md](SUBMISSION.md) "What the loop found", [toolbox/verdict.py](toolbox/verdict.py) |
| RIKEN Split A points the wrong way | M1 D1 = -0.069 (r(TASK,PRE) 0.222 > r(TASK,POST) 0.153), M2 D2 = -0.026, M3 D3 = -0.146, M4 D4 = -0.061, all p_N1 = 1.0 | [results/real/](results/real/) `M*_splitA.json` |
| RIKEN Split B | M1 D1 = +0.006, p_N1 = 0.19; M2 p_N1 = 0.002 but p_blockswap = 0.25 and M2 fails its control; M3, M4 ineligible (651 TASK frames < 1500) | [results/real/](results/real/) `M*_splitB.json` |
| Positive control, DANDI:000044 | M3 "yes" in 8/8 sessions (D3 = +0.028 to +0.144, p_N1 = 0.002 each); M4 same direction 8/8 | [results/real/dandi/summary.csv](results/real/dandi/summary.csv) |
| Spike-era bound fails on calcium | Marchenko-Pastur flags at least 5 false components in 50/50 synthetic noise runs; N1 flags at least one in 2/50 | [journal/engineer-b.md](journal/engineer-b.md) T-N1-8, [results/figures/eigenvalue_bounds.png](results/figures/eigenvalue_bounds.png) |
| Methods that fail their own tests | M2: 6/10 false "yes" with pre-existing assemblies; M4: T-M4-1 PCA 0.817 vs < 0.8 required; thresholds not moved | [tests/test_m2.py](tests/test_m2.py), [journal/engineer-b.md](journal/engineer-b.md) Entry 2 |

Limits: one RIKEN session, one animal, no behavioural task (a wake bout stands in for TASK), answer key signed by the team lead without a scientist sign-off ([PROBLEM.md](PROBLEM.md) "Signature").
Every prediction is committed before its run and every failure stays in [JOURNAL.md](JOURNAL.md).

## Research loop

Diagram: [research/research-loop.png](research/research-loop.png).

1. Read: literature and dataset search, distilled into [research/](research/) ([research/source-of-truth.md](research/source-of-truth.md), [research/CALCIUM_METHODS.md](research/CALCIUM_METHODS.md), [research/datasets/calcium-vetting.md](research/datasets/calcium-vetting.md)).
2. Lock: [PROBLEM.md](PROBLEM.md), the question and the answer key (number, unit, threshold per method), fixed before any real-data result and signed by the team lead.
3. Referee: tests with fixed thresholds, written before the code ([tests/referee/](tests/referee/), [tests/](tests/)).
4. Loop per task in [TASKS.md](TASKS.md): READ -> PREDICT -> RUN (test first) -> JUDGE -> RECORD.
5. Record: [JOURNAL.md](JOURNAL.md), append-only, one entry per step, each labelled verified, contradicted or not enough evidence.
   A finding is a number with a result file only.

## Layout

```text
PROBLEM.md              question and answer key, signed by the team lead (see its Signature section)
TASKS.md                ordered loop task list with owners
JOURNAL.md              append-only notebook; journal/engineer-b.md holds Engineer B's full counts
SUBMISSION.md           submission text for the lab's issue template
DEMO.md                 3-minute demo script
run.py                  one command: RIKEN .mat -> results/real/*.json (method tests and verdict not yet wired in)
pyproject.toml, uv.lock numpy, scipy, scikit-learn, h5py; pytest for tests
toolbox/
  contract.py           shared data contract (Recording) and return type (MethodResult)
  loader.py             RIKEN loader -> Recording per split            (A)
  loader_dandi.py       DANDI:000044 streaming loader (positive control)
  m1_pair_corr.py       M1 cell-pair correlation                        (A)
  m2_ev_rev.py          M2 EV vs. REV                                   (A)
  nulls.py              N1 circular-shift null, p-values, seeded streams (B)
  assemblies.py         z-score, eigen, projectors, R(t), N1 eigen bound (B)
  m3_pca.py             M3 PCA reactivation strength                    (B)
  m4_ica.py             M4 ICA reactivation strength                    (B)
  synth.py              synthetic calcium-like data for method tests    (B)
  controls.py           positive / negative control runs                (B)
  verdict.py            verdict rule                                    (Zixi)
scripts/                run_dandi.py (positive control), plot_referee.py (figures), per-method runners
tests/                  test-first: one test file per module; tests/referee/ planted-truth cases
results/
  real/                 RIKEN results per method and split; real/dandi/ positive control
  loader/               frame counts per split
  figures/              figures and the command that draws them (results/figures/README.md)
research/               literature, datasets, source of truth
plans/                  engineer plans
```

The package follows the file layout of [plans/engineer-b.md](plans/engineer-b.md) section 3, as a flat `toolbox/` package: `src/reactivation/<module>.py` there is `toolbox/<module>.py` here, imported as `toolbox.<module>`.

## Run

Python 3.12 via `uv`; no API keys.
The data is not in this repository.

```bash
# data: RIKEN CBS, Zenodo 17667863, CC BY 4.0 (1.9 GB zip)
curl -L --fail --output mouse_data.zip \
  "https://zenodo.org/records/17667863/files/mouse_data.zip?download=1"
unzip mouse_data.zip mouse_data/sleep_data.mat

# tests (fast; add -m slow for the 50-seed counted method tests)
uv run --python 3.12 --group dev pytest -m "not slow"

# every RIKEN result file, seed 0, 500 N1 shuffles -> results/real/
uv run --python 3.12 python run.py --data mouse_data/sleep_data.mat --seed 0

# positive control: M3 and M4 on the 8 DANDI:000044 sessions (streamed) -> results/real/dandi/
OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi.py --seed 0

# figures -> results/figures/
uv run --python 3.12 --with matplotlib python scripts/plot_referee.py
```

## License

- **Code** is licensed under the [Apache License 2.0](LICENSE).
- **Written material** (problem description, journal, results summaries and other documentation) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CC-BY-4.0).

This follows the default of the [Claude Impact Lab rules](https://github.com/xemantic/claude-impact-lab-2026).
Third-party papers and datasets keep their own licenses; see [research/papers/README.md](research/papers/README.md).
