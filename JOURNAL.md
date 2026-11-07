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

