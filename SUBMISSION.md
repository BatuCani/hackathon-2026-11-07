# Submission

Full text of every field of the lab's [project-submission template](https://github.com/xemantic/claude-impact-lab-2026/blob/main/.github/ISSUE_TEMPLATE/project-submission.yml), filled from this repository.
The captain copies it into the issue; this file is not the issue.
Numbers last synced from [results/real/](results/real/) at the time of the commit that last changed this file.

## Title

`[Submission] TEAM_NAME: Calcium sleep reactivation toolbox - four methods, one locked answer key, an honest "not enough evidence"`

## Team name

TEAM_NAME

## Team members

ROLES

- Batu (@BatuCani), Engineer A (loader, M1, M2, one-command repro)
- youssef-110 (@youssef-110), Engineer B (N1 null, M3 PCA, M4 ICA, synthetic data and controls)
- Zixi, criterion and verdict rule
- SCIENTIST_NAME, scientist, problem owner

## Field

Neuroscience

## Repository

https://github.com/BatuCani/hackathon-2026-11-07

## License

Apache 2.0 for code ([LICENSE](LICENSE)), CC BY 4.0 for text ([LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0)).

## Open problem

Neurons that fire together during a task tend to fire together again in the sleep that follows ("reactivation").
It is tested on the same neurons in sleep before the task (PRE), the task (TASK) and sleep after it (POST): reactivation means POST resembles TASK more than PRE does.
Question and answer key: [PROBLEM.md](PROBLEM.md); background: [research/team-brief.md](research/team-brief.md).

Why it is still open:
the standard methods (cell-pair correlation, explained variance vs. reverse, PCA and ICA assembly strength; Tingley and Peyrache 2020) were built for sparse electrophysiology spikes.
Two-photon calcium data is slow, so neighbouring frames are correlated and tests built for spikes can be too lenient.
Tingley and Peyrache also show that the methods often disagree on the same data.
There is no shared tool that says which methods a calcium dataset can support and how likely it is that it shows reactivation.

Why it matters:
calcium imaging records thousands of identified cells across days, far more than electrodes, so a trustworthy reactivation test on calcium data would open sleep-and-memory questions at a scale electrophysiology cannot reach.

How it is checked computationally:
every method returns one number with a unit and a one-sided p against a fixed null (N1: each neuron's trace circularly shifted by its own random offset, 500 times, seed 0).
The "yes" threshold for each method was written in [PROBLEM.md](PROBLEM.md) before any real-data result.
A method counts toward the verdict only if it passes positive and negative controls on synthetic calcium-like data with planted truth ([tests/referee/](tests/referee/), [toolbox/synth.py](toolbox/synth.py), [toolbox/controls.py](toolbox/controls.py)).

## The research loop

Diagram: [research/research-loop.png](research/research-loop.png).
State lives in files, not in a chat session.

1. **Read the literature.**
   Anchor paper Tingley and Peyrache 2020, plus calcium-specific methods and datasets, distilled into [research/source-of-truth.md](research/source-of-truth.md), [research/CALCIUM_METHODS.md](research/CALCIUM_METHODS.md), [research/briefing.md](research/briefing.md) and [research/papers/README.md](research/papers/README.md) (licence check per paper).
   Dataset search over DANDI, CRCNS, GIN, Zenodo, figshare, Dryad and OSF: [research/datasets/README.md](research/datasets/README.md); the chosen RIKEN file was downloaded and opened directly: [research/datasets/calcium-vetting.md](research/datasets/calcium-vetting.md).
   DANDI:000044 (rat CA1, electrophysiology) is used only as a positive control for the methods, not as a biological comparison to the RIKEN mouse cortex calcium data (species, region, modality and task all differ).
2. **Lock the question.**
   [PROBLEM.md](PROBLEM.md) fixes the data, splits, null model, one number, unit and "yes" threshold per method, and the overall verdict rule, before any result.
3. **Write the referee before the code.**
   [tests/referee/](tests/referee/) runs every method on four planted-truth synthetic cases (reactivation, noise, pre-existing assemblies, firing-rate confound) with fixed pass counts ([tests/referee/README.md](tests/referee/README.md)).
   Per-module tests: [tests/](tests/) (test_n1.py, test_m2.py, test_m3.py, test_m4.py, test_verdict.py and others).
4. **Run the loop per task** in [TASKS.md](TASKS.md): READ -> PREDICT -> RUN (test first) -> JUDGE -> RECORD.
   Each prediction is committed before its run, so it cannot be fitted afterwards (see the PREDICT and RECORD pairs in [JOURNAL.md](JOURNAL.md), e.g. "PREDICT T5 real data" 15:47 and "RECORD T5 real data" 15:48).
5. **Write and run the code.**
   [toolbox/](toolbox/): `loader.py` (RIKEN .mat -> `Recording` per split), `nulls.py` (N1), `assemblies.py` (z-score, eigen, N1 eigenvalue bound), `m1_pair_corr.py`, `m2_ev_rev.py`, `m3_pca.py`, `m4_ica.py`, `verdict.py`; one command [run.py](run.py) writes [results/real/](results/real/).
6. **Check its own results.**
   Each method's answer counts only if its controls pass ([toolbox/verdict.py](toolbox/verdict.py) `compute_verdict`); each journal entry is labelled verified, contradicted or not enough evidence, failures included.
7. **Record.**
   [JOURNAL.md](JOURNAL.md) is append-only (pen, no eraser) and [journal/engineer-b.md](journal/engineer-b.md) holds Engineer B's full counts; a finding is a number with a result file, nothing else.

## What the loop found

Data: one RIKEN CBS session (mouse05), the 300 most active of 6,920 cells, NREM frames only in PRE and POST, a wake bout as TASK, two splits ([PROBLEM.md](PROBLEM.md), [results/loader/frame_counts.json](results/loader/frame_counts.json)).

**Overall verdict, by the locked rule: not enough evidence** (provisional until `toolbox/verdict.py` writes it to [results/real/](results/real/); hand-applied here).
Only M1 is counted in both splits (M3 is eligible in Split A only; M2 and M4 fail their method tests), and the rule needs at least two.
No counted method says "yes" in either split: how likely = 0/2 in Split A (M1, M3), 0/1 in Split B (M1).

Per method, on real data, 500 N1 shuffles, seed 0 (figure: [results/figures/real_scores.png](results/figures/real_scores.png)):

| Method | Split A | Split B | Counts toward the verdict? | Result files |
|---|---|---|---|---|
| M1 cell-pair correlation | D1 = -0.069, p_N1 = 1.0 | D1 = +0.006, p_N1 = 0.19 | yes: passes referee cases a-d, eligible in both splits | [M1_splitA.json](results/real/M1_splitA.json), [M1_splitB.json](results/real/M1_splitB.json) |
| M2 explained variance vs. reverse | D2 = -0.026, p_N1 = 1.0 | D2 = +0.0017, p_N1 = 0.002, p_blockswap = 0.25 | no: fails its pre-existing control (6/10 false "yes") | [M2_splitA.json](results/real/M2_splitA.json), [M2_splitB.json](results/real/M2_splitB.json), [M2_verdict.json](results/real/M2_verdict.json) |
| M3 PCA reactivation strength | D3 = -0.146, p_N1 = 1.0 (15 significant components) | not eligible: TASK frames 651 < 1500 | passes its method tests; eligible in Split A only | [M3_splitA.json](results/real/M3_splitA.json), [M3_splitB.json](results/real/M3_splitB.json) |
| M4 ICA reactivation strength | D4 = -0.061, p_N1 = 1.0 | not eligible: TASK frames 651 < 1500 | no: fails T-M4-1 (PCA 0.817 vs < 0.8 required) | [M4_splitA.json](results/real/M4_splitA.json), [M4_splitB.json](results/real/M4_splitB.json) |

In words:

- In Split A, all four methods point the wrong way: TASK patterns are expressed more strongly in sleep **before** the wake bout than after it (M1 and M2: r(TASK, PRE) 0.222 > r(TASK, POST) 0.153; M1 D1 = -0.069; M3 and M4: D < 0; all p_N1 = 1.0).
- In Split B, M1 is slightly positive (D1 = +0.006) but not significant (p_N1 = 0.19).
- TASK patterns are significantly expressed in PRE and in POST each on its own (M3 p_n1_pre_alone = p_n1_post_alone = 0.002), so co-activity structure is real, but it is not specific to sleep after the wake bout.
- The one nominal "yes" (M2 Split B, p_N1 = 0.002 on D2 = 0.0017) is exactly the failure mode M2 showed on synthetic data with assemblies already present in PRE; the block-swap null does not support it (p = 0.25).

**Positive control on real data, DANDI:000044** ([research/datasets/ephys.md](research/datasets/ephys.md), [scripts/run_dandi.py](scripts/run_dandi.py), JOURNAL.md "PREDICT positive control on real data, DANDI:000044" 16:03).
DANDI:000044 (rat CA1, electrophysiology) is used only as a positive control for the methods, not as a biological comparison to the RIKEN mouse cortex calcium data (species, region, modality and task all differ).
The pass rule was fixed before the run: M3 says "yes" in at least 6 of the 8 sessions (8 sessions, 41-120 pyramidal units, 100 ms bins, all MAZE bins as TASK); fewer would mean the toolbox misses established reactivation, and the RIKEN "no" would carry that caveat.
Result: DANDI_PENDING (run in progress; results will be in [results/real/dandi/](results/real/dandi/)).

Methodological finding on synthetic calcium-like data (tau 1 s, no assemblies, 50 seeds; [journal/engineer-b.md](journal/engineer-b.md), JOURNAL.md "RECORD T4"):
the analytical Marchenko-Pastur bound, the usual way to pick significant PCA components from spike data, flags at least 5 false components in **50/50** runs; the N1 shuffle bound flags at least one in **2/50** (T-N1-8).
Figure: [results/figures/eigenvalue_bounds.png](results/figures/eigenvalue_bounds.png) (seed 0: 14 eigenvalues above Marchenko-Pastur, 0 above N1).
Calcium autocorrelation breaks the analytical bound, which is the brief's "tests built for spikes can be too lenient" concern made concrete.
The same N1 null still gives M3 7/50 false positives when assemblies already exist in PRE, which is why a block-swap p is reported next to it.

Method controls for M3 and M4 at a glance: [results/figures/controls_m3_m4.png](results/figures/controls_m3_m4.png); all figures and the command that draws them: [results/figures/README.md](results/figures/README.md).

How it was verified:
every prediction was committed before its run (JOURNAL.md PREDICT entries);
the frame counts reproduce the vetting report exactly ([tests/test_loader.py](tests/test_loader.py));
M3 passes T-A1 to T-A5 and T-M3-1 to T-M3-8 (positive 50/50, reversal 50/50);
no threshold or parameter was changed after a run.

Confidence:
high that this pipeline, on this one session, does not show reactivation under the locked keys;
low that this says anything about reactivation in general, because there is one session, one animal, and no real task.

## Where it got stuck

- **One session, no task.** The Zenodo archive holds one sleep session (mouse05), not the six the paper describes ([research/datasets/calcium-vetting.md](research/datasets/calcium-vetting.md)); there is no behavioural task, so a wake bout stands in for TASK. Nothing was learned during "TASK", so a negative result is the expected one, and the toolbox could not be tested on a positive real case.
- **M2 fails its own controls.** With the locked N1 rule M2 says "yes" in 6/10 synthetic pre-existing-assembly sessions (prediction was at most 2/10); adding a block-swap null fixes that but drops the positive control to 8/10 (< 9/10). Both are strict xfails, thresholds unchanged ([tests/test_m2.py](tests/test_m2.py), JOURNAL.md "RECORD T5" 15:50). M2 does not count.
- **M4 fails T-M4-1.** ICA should separate overlapping assemblies where PCA fails; on seed 0 ICA reaches 0.911 but PCA reaches 0.817, so the "PCA < 0.8" half fails; over seeds 0-9 ICA reaches 0.9 in only 5/10 ([journal/engineer-b.md](journal/engineer-b.md) Entry 2). The threshold was not moved. M4 does not count.
- **Split B is ineligible for M3 and M4.** 651 TASK frames < 5 x 300 cells; the rule was not relaxed after seeing the data ([results/real/M3_splitB.json](results/real/M3_splitB.json)). This leaves M3 scorable in one split only, so it cannot meet "yes in each split" either way.
- **M2 needs at least two sessions;** splits A and B are two pseudo-sessions of the same recording, so even a "yes" would not be independent replication (caveat in every M2 result file).
- **The answer key is not signed.** [PROBLEM.md](PROBLEM.md) still shows an empty scientist signature block (SIGNATURE_STATUS); the open choices (TASK frames, cell selection, block-swap) were decided by the team lead at 15:45 CET before any real-data result, and the referee in [tests/referee/](tests/referee/) is still marked PROPOSED.
- **Predictions that failed.** M1 was predicted negative in both splits and came out slightly positive in Split B; M2 was predicted "yes" in both splits and said "no" (JOURNAL.md "RECORD T2 real data", "RECORD T5 real data", both labelled contradicted).
- **Loop wiring.** [run.py](run.py) runs the methods and writes byte-identical results on synthetic data ([tests/test_run.py](tests/test_run.py)); the method tests are not yet wired into the same command, and the M3/M4 real-data run used a scratch script calling the same `toolbox` functions (JOURNAL.md "RECORD T3/T6 real data").

## What it would need next

- **Data:** sessions with a real task and sleep on both sides, ideally several animals: the other RIKEN sessions (the archive ships only one), or calcium data with learning between sleep bouts. A known-positive real dataset would let the referee be checked on real data, not only synthetic.
- **Methods:** a null that keeps calcium autocorrelation and breaks only the PRE/POST assignment for M2 (block-swap at the right block length), a second ICA test seed sweep to decide whether T-M4-1's threshold or ICA's setup is wrong, and M5-M8 (replay, sequence methods) from the team brief.
- **Eligibility:** a principled cell-selection rule (or dimensionality reduction) so short TASK bouts like Split B's are not lost; today it is "300 most active cells".
- **Expertise:** the scientist's sign-off on the answer key and the referee thresholds, and a sleep-physiology check of the NREM scoring at bout edges.
- **Loop:** wire method tests and the verdict into `run.py`, so one command goes from the .mat file to the verdict.

## How to run it

```shell
git clone https://github.com/BatuCani/hackathon-2026-11-07
cd hackathon-2026-11-07

# data: RIKEN CBS, Zenodo 17667863, CC BY 4.0 (1.9 GB zip, not in the repo)
curl -L --fail --output mouse_data.zip \
  "https://zenodo.org/records/17667863/files/mouse_data.zip?download=1"
unzip mouse_data.zip mouse_data/sleep_data.mat

# tests (fast; add -m slow for the 50-seed counted method tests)
uv run --python 3.12 --group dev pytest -m "not slow"

# every result file, seed 0, 500 N1 shuffles -> results/real/
uv run --python 3.12 python run.py --data mouse_data/sleep_data.mat --seed 0
```

Python 3.12 via `uv`; dependencies numpy, scipy, scikit-learn, h5py ([pyproject.toml](pyproject.toml), [uv.lock](uv.lock)).
No API keys are needed.

## Data and sources

- **Data:** Oomoto, Kiyooka, Oizumi, Murayama, *Single-cell calcium imaging dataset of large-scale neuronal activity across wakefulness, sleep, and anesthesia*, RIKEN CBS, [10.60178/cbs.20260708-001](https://doi.org/10.60178/cbs.20260708-001), Zenodo copy [10.5281/zenodo.17667863](https://doi.org/10.5281/zenodo.17667863), CC BY 4.0. Public mouse data; not committed here.
- **Positive-control data:** DANDI:000044 ([dandiarchive.org/dandiset/000044](https://dandiarchive.org/dandiset/000044)), rat CA1 electrophysiology (the Grosmark and Buzsaki 2016 recordings), streamed by [toolbox/loader_dandi.py](toolbox/loader_dandi.py), not committed. DANDI:000044 (rat CA1, electrophysiology) is used only as a positive control for the methods, not as a biological comparison to the RIKEN mouse cortex calcium data (species, region, modality and task all differ).
- **Anchor paper:** Tingley D., Peyrache A. (2020), On the methods for reactivation and replay analysis, Phil. Trans. R. Soc. B 375: 20190231, [10.1098/rstb.2019.0231](https://doi.org/10.1098/rstb.2019.0231). All rights reserved, linked and quoted, not copied.
- **Other papers and their licences:** [research/papers/README.md](research/papers/README.md) (only redistributable PDFs are committed); datasets considered and rejected: [research/datasets/README.md](research/datasets/README.md).
- The authors' MATLAB loader (oizumi-lab/mouse_network_2P, no licence) was read as a reference only, not copied.

## How Claude was used

- **Claude Code** (Claude Opus) for nearly all code, tests, literature notes and the journal, run by each engineer.
- **Parallel agents:** Engineer A ran an orchestrator that dispatched one Claude Code worker per task (loader, M2, M3/M4 real-data run, verdict, this submission) in isolated git worktrees, each following READ -> PREDICT -> RUN -> JUDGE -> RECORD and writing to [JOURNAL.md](JOURNAL.md).
- **Literature and dataset search:** Claude subagents searched DANDI, CRCNS, GIN, Zenodo, figshare, Dryad, OSF and paper data statements, then downloaded and opened the chosen file ([research/datasets/](research/datasets/), [research/findings/](research/findings/)).
- **Humans decided:** the question, the answer key, the cell-selection and TASK decisions ([PROBLEM.md](PROBLEM.md)), and which failures stay failures.

## Demo materials

[DEMO.md](DEMO.md) (3-minute script), figures in [results/figures/](results/figures/), loop diagram [research/research-loop.png](research/research-loop.png).

## Confirmations

- [ ] The repository is public and has an open-source license.
- [ ] The submission contains no secrets, API keys or non-anonymized private data.
- [ ] We agree that this submission text is published under CC BY 4.0, like the other written material in this repository.
