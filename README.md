# Reactivation toolbox

Claude Impact Lab hackathon project, 2026-11-07.

A toolbox that imports deconvolved two-photon calcium activity with its sleep stages, runs only the reactivation methods the data can support, and states how likely it is that the data show reactivation.
Reactivation means sleep after a task (POST) resembles the task (TASK) more than sleep before it (PRE) does.
PRE and POST use NREM frames only.

- Methods (Tingley & Peyrache 2020): M1 cell-pair correlation, M2 explained variance vs. reverse, M3 PCA reactivation strength, M4 ICA reactivation strength.
- Null model N1: each neuron's trace shifted by its own random circular offset, 500 times; every method reports p against N1.
- Data: RIKEN CBS, Zenodo 17667863, `mouse_data/sleep_data.mat` (CC BY 4.0), with a wake bout between two NREM periods standing in for TASK.
  The data is not in this repository.

Background and decisions: [research/team-brief.md](research/team-brief.md), [research/source-of-truth.md](research/source-of-truth.md), [research/datasets/calcium-vetting.md](research/datasets/calcium-vetting.md), [plans/engineer-b.md](plans/engineer-b.md).

## Research loop

Diagram: [research/research-loop.png](research/research-loop.png).

1. [PROBLEM.md](PROBLEM.md): the question and the answer key (number, unit, threshold per method), signed by the scientist and locked before any result.
2. Referee: tests with fixed thresholds, written before the code.
3. Loop per task in [TASKS.md](TASKS.md): READ -> PREDICT -> RUN (test first) -> JUDGE -> RECORD.
4. [JOURNAL.md](JOURNAL.md): append-only notebook, one entry per step, each labelled verified, contradicted or not enough evidence.
5. Findings are numbers with a result file only.

## Layout

```text
PROBLEM.md              question and answer key (DRAFT until signed)
TASKS.md                ordered loop task list with owners
JOURNAL.md              append-only notebook
run.py                  one-command repro (stub, task T8)
pyproject.toml          numpy, scipy, scikit-learn, h5py; pytest for tests
toolbox/
  contract.py           shared data contract (Recording) and return type (MethodResult)
  loader.py             RIKEN loader -> Recording per split            (A)
  m1_pair_corr.py       M1 cell-pair correlation                        (A)
  m2_ev_rev.py          M2 EV vs. REV                                   (A)
  nulls.py              N1 circular-shift null, p-values, seeded streams (B)
  assemblies.py         z-score, eigen, projectors, R(t), N1 eigen bound (B)
  m3_pca.py             M3 PCA reactivation strength                    (B)
  m4_ica.py             M4 ICA reactivation strength                    (B)
  synth.py              synthetic calcium-like data for method tests    (B)
  controls.py           positive / negative control runs                (B)
  verdict.py            verdict rule                                    (Zixi)
tests/                  test-first: one test file per module
research/               literature, datasets, source of truth
plans/                  engineer plans
```

The package follows the file layout of [plans/engineer-b.md](plans/engineer-b.md) section 3, as a flat `toolbox/` package: `src/reactivation/<module>.py` there is `toolbox/<module>.py` here, imported as `toolbox.<module>`.

## Run

```bash
uv run --group dev pytest
uv run python run.py --data /path/to/sleep_data.mat --seed 0
```

## License

- **Code** is licensed under the [Apache License 2.0](LICENSE).
- **Written material** (problem description, journal, results summaries and other documentation) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CC-BY-4.0).

This follows the default of the [Claude Impact Lab rules](https://github.com/xemantic/claude-impact-lab-2026).
Third-party papers and datasets keep their own licenses; see [research/papers/README.md](research/papers/README.md).
