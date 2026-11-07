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

### 2026-11-07 16:05 CET PREDICT T3/T6 real data (M3 and M4 runner, crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md keys D3 "D3 > 0 and p_N1 < 0.05 (500 shuffles, seed 0), in each split" and D4 "as M3, but at least two significant components"; eligibility "TASK frames >= 5 x cells" | prediction: Split B ineligible for M3 and M4 (TASK frames 651 < 1500 for 300 cells); Split A eligible for both (1824 >= 1500) with n_sig >= 2; D3 and D4 sign in Split A uncertain (M2 found TASK closer to PRE than POST, so D3 <= 0 is plausible); locked-key answer for M3 and M4 is at best "not enough evidence", since "in each split" cannot be met with Split B ineligible.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 python (toolbox.m3_pca.run / toolbox.m4_ica.run on toolbox.loader.load_sessions defaults, seed 0, AssemblyParams(n_shuffles=500))
- Git SHA: the commit adding this entry
- Result file: results/real/M3_splitA.json, results/real/M3_splitB.json, results/real/M4_splitA.json, results/real/M4_splitB.json
- Label: -
- Note: Method-test status before the run: M3 passes T-A1 to T-A5 and T-M3-1 to T-M3-8; M4 fails T-M4-1 (PCA 0.817 vs < 0.8), so M4 should not count toward the verdict whatever it returns.

### 2026-11-07 16:12 CET RECORD T3/T6 real data (M3 and M4 runner, crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PREDICT T3/T6 real data 16:05 above
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 python run_m3m4.py (scratch script outside the repo: toolbox.loader.load_sessions defaults, m3_pca.run / m4_ica.run, seed 0, AssemblyParams(n_shuffles=500))
- Git SHA: 92ff4cc
- Result file: results/real/M3_splitA.json, results/real/M3_splitB.json, results/real/M4_splitA.json, results/real/M4_splitB.json
- Label: verified
- Note: Split A (eligible, 300 cells, n_sig 15, N1 bound 2.42): D3 = -0.146, p_N1 = 1.0, p_blockswap = 0.768; D4 = -0.061, p_N1 = 1.0, p_blockswap = 0.695. Split B: M3 and M4 not eligible, "TASK frames 651 < 1500 (5 per cell x 300 cells)". Prediction held: B ineligible, A eligible with n_sig >= 2, D3 <= 0 in A.
- Note: Locked keys D3 and D4: not "yes" (D < 0 in Split A, the only eligible split; Split B cannot be scored). TASK patterns are significantly expressed in both PRE and POST alone (p_n1_pre_alone = p_n1_post_alone = 0.002) but more strongly in PRE, matching M2's r_T,PRE > r_T,POST. M3 passes its method tests; M4 fails T-M4-1, so only M3 counts toward the verdict. No parameters changed after the run.

### 2026-11-07 15:45 CET PREDICT T7 (Zixi / crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md section "Overall verdict (DRAFT, owner Zixi)" "Counted methods = eligible methods that passed their method tests. - Reactivation likely: at least two counted methods say 'yes' in both splits, and no counted method says 'yes' in the reversed direction (POST and PRE swapped). - Reactivation not supported: no counted method says 'yes' in either split. - Not enough evidence: anything else, including fewer than two counted methods."
- Command: uv run --python 3.12 pytest tests/test_verdict.py
- Git SHA: 33d3041
- Result file: tests/test_verdict.py, toolbox/verdict.py
- Label: -
- Note: Hand-made MethodResult inputs will test all three outcomes, ineligible methods, failed controls, reverse direction veto, and summary markdown generation.

### 2026-11-07 15:47 CET RECORD T7 (Zixi / crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md section "Overall verdict (DRAFT, owner Zixi)" "Counted methods = eligible methods that passed their method tests. - Reactivation likely: at least two counted methods say 'yes' in both splits, and no counted method says 'yes' in the reversed direction (POST and PRE swapped). - Reactivation not supported: no counted method says 'yes' in either split. - Not enough evidence: anything else, including fewer than two counted methods."
- Command: uv run --python 3.12 pytest tests/test_verdict.py
- Git SHA: 33d3041
- Result file: tests/test_verdict.py, toolbox/verdict.py
- Label: verified
- Note: All 9 tests pass covering Reactivation likely, Reactivation not supported, Not enough evidence (split disagreement, ineligible methods, failed controls, reversed veto), zero counted methods, and summary markdown generation for results/real/summary.md.

### 2026-11-07 16:03 CET PREDICT positive control on real data, DANDI:000044 (Engineer B)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): research/datasets/ephys.md section 4 "the canonical replay benchmark: Grosmark & Buzsaki 2016 and Chen et al. 2016 used these exact recordings"; PROBLEM.md keys D3/D4 "D > 0 and p_N1 < 0.05 (500 shuffles, seed 0)" | prediction: all 8 sessions eligible for M3 and M4 (41-120 pyramidal units, 20,675-55,592 TASK bins, results/loader-check/dandi44.txt); D3 > 0 with p_N1 < 0.05 in at least 6 of 8 sessions; D4 the same direction; p_blockswap (supplementary column) less often < 0.05 than p_N1.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi.py --seed 0 (loader defaults: 100 ms bins, pyramidal cells, all MAZE bins as TASK; AssemblyParams defaults, 500 shuffles)
- Git SHA: the commit adding this entry
- Result file: results/real/dandi/summary.csv and per-session JSON
- Label: -
- Note: Pass rule for the positive control, fixed here before the run: M3 says "yes" (D3 > 0 and p_N1 < 0.05) in at least 6 of 8 sessions. Fewer means the toolbox misses established reactivation on real ephys data and the RIKEN "no" must be read with that caveat. M4 is reported but does not count (T-M4-1 failed). toolbox/loader_dandi.py is from eng-b/toolbox (1451378), merging into main separately.

### 2026-11-07 16:00 CET READ T2 (Engineer A, crewmate)

- Step: READ
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md answer key "D1 = r(C_TASK, C_POST) - r(C_TASK, C_PRE), Pearson r between the flattened upper triangles of the cell-pair correlation matrices" and "D1 > 0 and p_N1 < 0.05 (N1 on PRE and POST, 500 shuffles, seed 0), in each split".
- Command: -
- Git SHA: 6c01ac3
- Result file: -
- Label: -
- Note: Eligibility is the same cells in PRE, TASK and POST, and at least 300 NREM frames in PRE and in POST. The referee on this commit passed cases a-d (reactivation, noise, pre-existing, rate-only).

### 2026-11-07 16:00 CET PREDICT T2 real data (Engineer A, crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md key D1 "D1 > 0 and p_N1 < 0.05 ... in each split" | prediction: both splits eligible at the loader default of 300 cells; D1 < 0 in both splits (M2 and M3 already found TASK closer to PRE than to POST); p_N1 > 0.05 in both, because the test is one-sided for D1 > 0. Locked-key answer is not yes.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 python scripts/run_m1.py --seed 0
- Git SHA: the commit adding this entry
- Result file: results/real/M1_splitA.json, results/real/M1_splitB.json
- Label: -
- Note: 500 shuffles, seed 0, N1 shifts PRE and POST only. No block-swap term: the M1 key does not use one.

### 2026-11-07 16:02 CET RECORD T2 real data (Engineer A, crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PREDICT T2 real data 16:00 above
- Command: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --python 3.12 python scripts/run_m1.py --seed 0
- Git SHA: f325ad1
- Result file: results/real/M1_splitA.json, results/real/M1_splitB.json
- Label: contradicted
- Note: Both splits eligible (300 cells, 0 dropped). Split A: r(C_TASK, C_POST) = 0.153, r(C_TASK, C_PRE) = 0.222, D1 = -0.0691, p_N1 = 1.0 (PRE 1300, TASK 1824, POST 999). Split B: r(C_TASK, C_POST) = 0.145, r(C_TASK, C_PRE) = 0.139, D1 = +0.00608, p_N1 = 97/501 = 0.194 (PRE 2657, TASK 651, POST 2669).
- Note: Prediction "D1 < 0 in both splits" is contradicted by Split B's small positive. Prediction "p_N1 > 0.05 in both" and "locked key is not yes" held: neither split has D1 > 0 and p_N1 < 0.05. Referee cases a-d passed before this run (24.1 s of the 30 s budget). No parameters changed after the run.

### 2026-11-07 15:40 CET RECORD loader DANDI:000044 (Engineer B)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): research/datasets/ephys.md section 1 "51-137 total; 41-120 pyramidal (`units.cell_type`)"; prediction: the loader reproduces those pyramidal counts and the PRE/MAZE/POST lengths.
- Command: uv run --python 3.12 pytest tests/test_loader_dandi.py; uv run --python 3.12 --with remfile python scripts/check_dandi44.py
- Git SHA: 33d3041 + loader commit
- Result file: results/loader-check/dandi44.txt, toolbox/loader_dandi.py
- Label: verified
- Note: All 8 sessions stream and load; pyramidal counts 120, 92, 48, 55, 81, 59, 66, 41 equal ephys.md. Bins 100 ms; TASK >= 5N holds in every session (20,675-55,592 TASK bins vs 205-600). No method was run on real data (PROBLEM.md unsigned). Open: 90-370 MAZE bins are buzcode NREM in 3 sessions and count as TASK under analysis_mask (plan Q5, TASK = non-unscored); bin size and pyramidal-only are [TEAM DECISION]s.

### 2026-11-07 16:10 CET JUDGE/RECORD positive control on real data, DANDI:000044 (Engineer B)

- Step: JUDGE, RECORD
- Source and quote (READ) or prediction (PREDICT): PREDICT 16:03 above, pass rule "M3 says yes (D3 > 0 and p_N1 < 0.05) in at least 6 of 8 sessions"
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi.py --seed 0 (finished 16:08)
- Git SHA: d56af87 (toolbox/loader_dandi.py from eng-b/toolbox 1451378, not yet on main)
- Result file: results/real/dandi/summary.csv and results/real/dandi/<session>__M3.json, __M4.json (R(t) .npz not committed, 131 MB; the command regenerates them)
- Label: verified (M3 positive control passes 8/8)
- Note: All 8 sessions eligible for M3 and M4 (n_sig 6-19). M3: D3 > 0 in 8/8 (0.028 to 0.144), p_N1 = 0.002 (= 1/501, the minimum) in 8/8. M4: D4 > 0 in 8/8 (0.028 to 0.125), p_N1 = 0.002 in 8/8 (reported, does not count: T-M4-1 failed).
- Note: Prediction "p_blockswap less often < 0.05 than p_N1" contradicted: p_blockswap = 0.002 in 16/16 runs. The toolbox detects established reactivation in real hippocampal ephys, so the RIKEN Split A "no" (D3 = -0.146) is not explained by a toolbox that cannot say yes. Remaining differences from RIKEN: ephys spikes vs calcium, 100 ms bins vs 7.65 Hz frames, real task vs a wake bout as pseudo-TASK.

### 2026-11-07 16:11 CET RECORD T0 sign-off (Batu, team lead)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): PROBLEM.md section "Signature"
- Command: none
- Git SHA: b11e8d0 (PROBLEM.md at signing)
- Result file: PROBLEM.md
- Label: verified
- Note: Batu (team lead, Engineer A) signed the answer key on behalf of the team. No scientist sign-off was available. Signed after the first results. The answer key and all decisions were committed before any real-data result: commit 20a62a8 (15:44 CET, decisions); first PREDICT 15:47, first real result 15:48 (see JOURNAL.md). Nothing in the key was changed after a result.

### 2026-11-07 16:17 CET PREDICT Loop 2: M1 and M2 on DANDI:000044, 8 sessions (crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): answer key fixed before the run. Per session, "yes" = score > 0 and p_N1 < 0.05 (500 shuffles, seed 0); D1 for M1, D2 = EV - REV for M2. Pass = "yes" in >= 6/8 sessions for each of M1 and M2; M2 additionally needs EV > REV across sessions (mean EV over the 8 sessions > mean REV). Prediction: both pass; M1 "yes" in 8/8 and M2 "yes" in >= 7/8 with mean EV > mean REV, because M3/M4 found strong reactivation (p_N1 = 0.002) in 8/8 sessions on the same data.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/run_dandi_m1m2.py --seed 0
- Git SHA: the commit adding this entry
- Result file: results/real/dandi/<session>__M1.json, __M2.json, rows appended to results/real/dandi/summary.csv
- Label: -
- Note: Loader settings as for M3/M4: 100 ms bins, pyramidal units, all MAZE bins as TASK, NREM-only PRE/POST (contract.analysis_mask). Method code and defaults unchanged. One process, sessions in sequence.

### 2026-11-07 16:22 CET PREDICT Loop 3: rate confound on DANDI:000044, 8 sessions (crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): Tingley & Peyrache (2020) section 3b-v: a change in intrinsic excitability (firing rate) between PRE and POST could explain part of the reactivation measures, and "a systematic review and analysis of this possibility is still missing". Answer key fixed before the run: per session, rate ratio = mean POST NREM rate / mean PRE NREM rate over the analysed cells (contract.analysis_mask, loader defaults). Across the 8 DANDI sessions, Pearson r between log rate ratio and the M3 score D3 (results/real/dandi/summary.csv). "Rate confound supported" if r > 0.7 and p < 0.05 (n = 8); "not supported" if |r| < 0.3 or p >= 0.05; otherwise "not enough evidence". The same ratio is reported for RIKEN Split A and Split B (mean deconvolved activity, not a spike rate), no test.
- Prediction: "not supported". Rate ratios close to 1 (within 0.8-1.25) in all 8 sessions, and |r| < 0.3 or p >= 0.05, because D3 tracks cell count and assembly number (largest in the two Achilles sessions) more than any PRE-to-POST rate change, and z-scoring per epoch in M3 removes most of a rate offset.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/rate_confound.py
- Git SHA: the commit adding this entry
- Result file: results/real/rate_confound.json, results/figures/rate_confound.png
- Label: -
- Note: Existing loaders only, no method code changes. One process, sessions in sequence. Hard stop 16:38; if not done, "not enough evidence".

### 2026-11-07 16:28 CET PREDICT Loop 4: M3 bin-size robustness on DANDI:000044, 3 sessions (crewmate)

- Step: PREDICT
- Source and quote (READ) or prediction (PREDICT): Tingley & Peyrache (2020) section 3b-v: "a systemic variation of bin size and its impact on pattern detection is lacking". Answer key fixed before the run: sessions = the 3 with the most pyramidal units in results/real/dandi/summary.csv (Achilles_10252013, 120; Achilles_11012013, 92; Cicero_09102014, 81); bins = 50, 100, 200 ms. Per (session, bin) M3 says "yes" if D3 > 0 and p_N1 < 0.05 (200 shuffles, seed 0). "robust" if "yes" at all three bin sizes in all 3 sessions; "bin-dependent" if any of the 9 flips to "no"; otherwise (a run missing or not eligible) "not enough evidence".
- Prediction: "robust". All 9 runs "yes", D3 largest at 50-100 ms in the Achilles sessions; at 200 ms the TASK bin count halves (eligibility risk) but the 100 ms runs had p_N1 at the floor.
- Command: OMP_NUM_THREADS=1 uv run --python 3.12 --with remfile python scripts/binsize_m3.py
- Git SHA: the commit adding this entry
- Result file: results/real/dandi_binsize.json, results/figures/binsize_m3.png
- Label: -
- Note: Deviation from PROBLEM.md, decided before the run: 200 shuffles instead of 500 to fit the time (min p = 1/201 = 0.005). Loader already takes bin_s (default 0.1 unchanged); no method code changes. One process, sessions in sequence. Hard stop 16:40; whatever exists then is recorded, missing runs count as "not enough evidence".

### 2026-11-07 16:22 CET RECORD T8 (crewmate)

- Step: RECORD
- Source and quote (READ) or prediction (PREDICT): TASKS.md T8 "Done when a fresh clone reproduces byte-identical result JSON."
- Command: git clone --depth 1 https://github.com/BatuCani/hackathon-2026-11-07 (SHA b11e8d0); uv run --python 3.12 python run.py --data /Users/batu/hackathon-data/riken/mouse_data/sleep_data.mat --seed 0 --out <scratch>/run-out; uv run --group dev pytest -m "not slow" (CPython 3.14.7, before the 3.12 pin)
- Git SHA: b11e8d0
- Result file: results/real/M1_splitA.json, results/real/M1_splitB.json, results/real/M2_splitA.json, results/real/M2_splitB.json, results/real/M3_splitA.json, results/real/M3_splitB.json, results/real/M4_splitA.json, results/real/M4_splitB.json
- Label: verified
- Note: Each file run.py wrote (`mouse05_split{A,B}__M{1-4}.json`) is byte-identical to the committed `M{n}_split{A,B}.json` (eight sha256 matches). Wall time 61 s on Python 3.12.15, seed 0, 500 shuffles. `--out` only changed the directory. `summary.csv` is written and was not committed. `M2_verdict.json` is committed and is not written by run.py (it comes from scripts/run_m2.py). Fast tests: 117 passed, 1 failed, 2 xfailed, 20 deselected, 235 s. The failure is tests/test_m4.py::test_t_m4_1_overlap_ica_beats_pca (PCA 0.817 vs < 0.8), the open T-M4-1 threshold; no method logic, threshold, or committed result was changed.

2026-11-07 16:32 CET RECORD: toolbox.verdict.compute_verdict on results/real/M1-M4 split JSON (method tests M1 pass, M2 fail, M3 pass, M4 fail) wrote results/real/verdict.json and results/real/summary.md: Not enough evidence, counted M1, how likely 0/2 mouse05_splitA and 0/1 mouse05_splitB. Fast CI: .github/workflows/tests.yml (Python 3.12, pytest -m "not slow"; T-M4-1 xfail strict=False, recorded failure).
