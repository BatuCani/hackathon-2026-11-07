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
