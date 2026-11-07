# Journal

Append-only research notebook: pen, no eraser.
Every loop step writes here, failures too.
Never edit or delete an entry; correct a mistake with a new entry that names the one it corrects.

## Loop

The answer key in [PROBLEM.md](PROBLEM.md) and the referee (tests and thresholds) are locked before any result.
Then each task in [TASKS.md](TASKS.md) runs the loop:

1. **READ**: the source, with a quote.
2. **PREDICT**: what the run will show, written and committed before the run.
3. **RUN**: the test first, then the code; the exact command, seed and git SHA.
4. **JUDGE**: which test or answer key decided, and how.
5. **RECORD**: the result file and one label.

Labels: **verified**, **contradicted**, **not enough evidence**.
Findings are numbers with a file only; a number without a result file in the repo is not a finding.

## Entry format

Copy this block for each step and fill in every field; write "-" for a field that does not apply.

```markdown
### <YYYY-MM-DD HH:MM CET> <STEP> <task id from TASKS.md> (<author>)

- Step: READ | PREDICT | RUN | JUDGE | RECORD
- Source and quote (READ) or prediction (PREDICT): <path or DOI, section> "<exact quote>" | <expected number, unit, direction>
- Command: <exact command, including seed>
- Git SHA: <commit the command ran on>
- Result file: <path in the repo>
- Label: verified | contradicted | not enough evidence | -
- Note: <one or two sentences, optional>
```

## Entries

### 2026-11-07 15:18 CET RECORD T0 (scaffold)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): research/team-brief.md section 1 "Reactivation means POST resembles TASK more than PRE does."
- Command: -
- Git SHA: -
- Result file: PROBLEM.md, TASKS.md
- Label: -
- Note: Loop files created; answer key is DRAFT and awaits the scientist's signature before any result.

### 2026-11-07 15:40 CET RECORD T4 (Engineer B)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): research/team-brief.md section 4 "shift each neuron's trace by its own random circular offset, 500 times; keeps each neuron's autocorrelation, breaks co-activity."
- Command: uv run --python 3.12 pytest -m slow (50 seeds, 200 shuffles); uv run --python 3.12 pytest -m "not slow"
- Git SHA: e91b67a (eng-b/n1-m3-m4); port to toolbox/ re-run with identical numbers
- Result file: journal/engineer-b.md (Entries 1-3, predictions and full counts), toolbox/nulls.py, toolbox/assemblies.py
- Label: verified
- Note: T-N1-1 to T-N1-9 pass. On synthetic data with tau 1 s and no assemblies, Marchenko-Pastur gives >= 5 false components in 50/50 seeds, the N1 bound gives >= 1 in 2/50.

### 2026-11-07 15:40 CET RECORD T3 (Engineer B)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): research/source-of-truth.md M4 "the diagonal of the projectors is set at 0"
- Command: as T4
- Git SHA: e91b67a
- Result file: journal/engineer-b.md Entry 3, toolbox/m3_pca.py
- Label: verified
- Note: T-A1 to T-A5 and T-M3-1 to T-M3-8 pass (positive 50/50; false positives 1/50, 3/50 with p_blockswap, 2/50; reversal 50/50). p_n1 alone gives 7/50 false positives when assemblies already exist in PRE.

### 2026-11-07 15:40 CET RECORD T6 (Engineer B)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): research/source-of-truth.md M6 "ICA ... successfully separates assemblies of coordinated neurons, even when assemblies have overlapping member neurons [20], a situation in which PCA fails"
- Command: as T4
- Git SHA: e91b67a
- Result file: journal/engineer-b.md Entries 2-3, toolbox/m4_ica.py
- Label: contradicted
- Note: T-M4-1 (seed 0) fails: ICA 0.911 passes, PCA 0.817 vs < 0.8 required; over seeds 0-9 ICA reaches 0.9 in 5/10. T-M4-2 to T-M4-4 pass. Threshold not changed.

### 2026-11-07 15:41 CET PREDICT T1 (Engineer A, crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): research/datasets/calcium-vetting.md "Recommended splits" | Split A: PRE NREM 1300 frames, TASK 1825 frames (1824 scored, frame 7305 is an interpolation value), POST NREM 999; Split B: PRE NREM 2657, TASK 651 (vetting text rounds to 650), POST NREM 2669; cells kept 300 (A) and 130 (B) under the PROPOSED cap TASK frames >= 5 x cells.
- Command: OMP_NUM_THREADS=2 uv run --python 3.12 pytest tests/test_loader.py
- Git SHA: 33d3041 (plus the uncommitted loader and test under test)
- Result file: -
- Label: -
- Note: Loader reads only spike, state, frame and ROIs (never dFF); authors' MATLAB loader (oizumi-lab/mouse_network_2P, no licence) used as reference only.

### 2026-11-07 15:45 CET RECORD T1 (Engineer A, crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md "Not decided yet" (decided by the team lead, commit 20a62a8) "the 300 most active cells by mean deconvolved activity (`spike`) over the union of both splits' TASK frames, so splits A and B use the same cells"
- Command: OMP_NUM_THREADS=2 uv run --python 3.12 pytest tests/test_loader.py tests/test_run.py; uv run --python 3.12 python -m toolbox.loader > results/loader/frame_counts.json
- Git SHA: 20a62a8 (plus the loader commit that adds this entry)
- Result file: results/loader/frame_counts.json
- Label: verified
- Note: Frame counts equal the 15:41 PREDICT entry: A PRE 1300, TASK 1825 (1824 scored), POST 999; B PRE 2657, TASK 651, POST 2669; 15 tests pass. This entry corrects the cell count in the 15:41 PREDICT entry: after the team-lead decision both splits keep the same 300 cells (not 300 and 130), so M3 and M4 report Split B not eligible ("TASK frames 651 < 1500 (5 per cell x 300 cells)"), checked by tests/test_loader.py.

### 2026-11-07 15:45 CET RECORD T8 partial (Engineer A, crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): TASKS.md T8 "python run.py --data <path to sleep_data.mat> --seed 0 writes every result file"
- Command: OMP_NUM_THREADS=2 uv run --python 3.12 pytest tests/test_run.py
- Git SHA: 20a62a8 (plus the loader commit that adds this entry)
- Result file: -
- Label: not enough evidence
- Note: run.py loads both splits, runs every method module that exposes run() (M3, M4 now; M1, M2 listed as not implemented) and writes results/real/<session>__<method>.json plus summary.csv; two runs on a synthetic .mat give byte-identical files. Not run on the real data: T0 (scientist's signature) is still open, and PROBLEM.md says no result is computed before it.
### 2026-11-07 15:35 CET PREDICT T5 (Engineer A, M2 worker)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): research/source-of-truth.md M2 "Reactivation can thus be assessed by a significant difference between EV and REV across recording sessions" | synthetic controls (toolbox/controls.py scenarios, tau 1 s, 200 shuffles, seeds 0-9): positive D2 > 0 with p_N1 < 0.05 in >= 9/10; no_sleep_coactivity, pre_existing, noise_only and reversed "yes" in <= 2/10; reversed gives D2 < 0.
- Command: uv run --python 3.12 pytest tests/test_m2.py -m "not slow"
- Git SHA: (this commit's parent, branch fm/hackathon-t5-m2)
- Result file: tests/test_m2.py, results/synthetic/M2_*.json
- Label: -
- Note: Loader (T1) is not on main, so no real-data run yet; only synthetic.

### 2026-11-07 15:50 CET RECORD T5 (Engineer A, M2 worker)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PREDICT T5 15:35 above
- Command: uv run --python 3.12 pytest tests/test_m2.py -m "not slow"; uv run --python 3.12 python scripts/run_m2.py --seed 0
- Git SHA: parent of the commit adding this entry (branch fm/hackathon-t5-m2)
- Result file: results/synthetic/M2_splitA.json, results/synthetic/M2_splitB.json, results/synthetic/M2_verdict.json, tests/test_m2.py
- Label: contradicted
- Note: Formula hand-checked (3x3 matrices give EV = REV = 1, since 3 pairs span 2 centered dimensions, hence min_cells = 4). With the locked rule (D2 > 0, p_N1 < 0.05), positive 10/10, no_sleep_coactivity, noise_only and reversed 0/10 each, but pre_existing 6/10 false "yes" (prediction <= 2/10 contradicted): N1 breaks PRE and POST co-activity alike, so its null sits near 0 while chance EV vs REV differences do not.
- Note: Added supplementary details.p_blockswap (20 s PRE/POST block labels permuted, as M3); with it pre_existing passes but positive drops to 8/10 (< 9/10). Both shortfalls are strict xfails, thresholds unchanged; M2 does not pass its method tests yet, so it should not count toward the verdict. No real-data run: the loader (T1) is not on main.

### 2026-11-07 15:47 CET PREDICT T5 real data (Engineer A, M2 worker)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md key D2 "D2 > 0 in both splits A and B, and p_N1 < 0.05 in each split" | prediction: D2 > 0 in both splits but small (< 0.05), p_N1 < 0.05 in both (N1 flagged pre-existing structure in the synthetic controls), p_blockswap >= 0.05 in at least one split; locked-rule answer "yes" with the two-pseudo-session caveat, which the failed pre_existing control makes uninterpretable on its own.
- Command: OMP_NUM_THREADS=2 uv run --python 3.12 python scripts/run_m2.py --data /Users/batu/hackathon-data/riken/mouse_data/sleep_data.mat --seed 0
- Git SHA: the commit adding this entry
- Result file: results/real/M2_splitA.json, results/real/M2_splitB.json, results/real/M2_verdict.json
- Label: -
- Note: Loader defaults (300 most active cells over both TASK bouts, PROBLEM.md decisions 15:45), 500 shuffles.

### 2026-11-07 15:48 CET RECORD T5 real data (Engineer A, M2 worker)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PREDICT T5 real data above
- Command: OMP_NUM_THREADS=2 uv run --python 3.12 python scripts/run_m2.py --data /Users/batu/hackathon-data/riken/mouse_data/sleep_data.mat --seed 0
- Git SHA: bd3d759
- Result file: results/real/M2_splitA.json, results/real/M2_splitB.json, results/real/M2_verdict.json
- Label: contradicted
- Note: Split A: EV 0.0153, REV 0.0414, D2 = -0.0261, p_N1 = 1.0 (r_T,PRE 0.222 > r_T,POST 0.153: TASK resembles PRE more than POST). Split B: EV 0.0133, REV 0.0116, D2 = +0.0017, p_N1 = 0.002, p_blockswap = 0.248. Locked key answer: "no" (D2 < 0 in split A); prediction "yes in both" contradicted.
- Note: Split B's p_N1 < 0.05 on a D2 of 0.002 is the pre_existing failure mode seen in the synthetic controls (N1 null q95 = 0.0001); M2 has not passed its method tests, so it should not count toward the verdict either way.
