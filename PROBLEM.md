# Problem

**Status: DRAFT - to be signed by the scientist before any result.**
No method result may be computed or read before the signature block at the end is filled in.
After signing, this file is frozen: changes only as a new dated section below the signature, never by editing the keys.

## The question, in the scientist's words

From [research/team-brief.md](research/team-brief.md), section 1 and the opening paragraph:

> Neurons that are active together during a task tend to be active together again in the sleep that follows.
> It is tested on the same neurons in three periods: sleep before the task (PRE), the task (TASK), and sleep after it (POST).
> Reactivation means POST resembles TASK more than PRE does.

> We build a toolbox that imports deconvolved neuronal activity with its sleep stages automatically, runs only the reactivation methods the data can support, and states how likely it is that the data show reactivation.

Today's concrete question:

1. In the RIKEN cortex data, does POST NREM resemble TASK more than PRE NREM does, separately for each method M1, M2, M3 and M4?
2. Taking only the methods that are eligible and pass their method tests, how likely is it that the data show reactivation overall?

## Data and fixed choices

- Dataset: RIKEN CBS, Zenodo record 17667863, file `mouse_data/sleep_data.mat`, CC BY 4.0.
  One session, mouse05, 6,920 cells x 19,000 frames, two discontinuous segments of 9,500 frames each.
  Verified contents: [research/datasets/calcium-vetting.md](research/datasets/calcium-vetting.md).
  The data is never committed to this repository.
- `deconv` = variable `spike` (raw OASIS deconvolution, never smoothed).
- `sleep_stage` from `state.state`: 0 and 0.5 -> wake, 1 -> NREM, 2 -> REM, other -> unscored.
- `fs` = 7.65 Hz, an external constant from the data description paper (not in the file).
- There is no behavioural task: a wake bout between two NREM periods stands in for TASK, as the team brief foresees (section 3).
- Two splits, each inside one recording segment (frame indices 0-based, from the vetting report):
  - **Split A** (segment 0): TASK = frames 5481-7306 (239 s wake), PRE = 1,300 NREM frames (170 s), POST = 999 NREM frames (131 s).
  - **Split B** (segment 1): TASK = frames 15006-15657 (85 s wake), PRE = 2,657 NREM frames (347 s), POST = 2,669 NREM frames (349 s).
- PRE and POST use NREM frames only (team brief section 4).
- Method IDs are the team-brief IDs (M3 = PCA, M4 = ICA), not the source-of-truth IDs; see [plans/engineer-b.md](plans/engineer-b.md) section 0.

## Null model N1 (shared by every key)

- Shift each neuron's trace by its own random circular offset, 500 times (team brief section 4).
- Shifts are done on the analysed frames of one split only, never across the segment boundary.
- One-sided p = (1 + number of shuffles with null score >= observed) / (1 + 500); smallest possible p = 1/501.
- Seed fixed: `seed = 0`, random streams derived from (seed, split id, purpose), as in [plans/engineer-b.md](plans/engineer-b.md) step 2.
- Significance level: alpha = 0.05, one-sided, per method and split.

## ANSWER KEY (DRAFT)

Each key gives the number, its unit, and the threshold for "yes".
A method that fails its requirement check is reported as **not eligible** with the missing data listed; it is not a "no".

| Method | Number | Unit | "Yes" threshold | Eligibility |
|---|---|---|---|---|
| M1 cell-pair correlation | D1 = r(C_TASK, C_POST) - r(C_TASK, C_PRE), Pearson r between the flattened upper triangles of the cell-pair correlation matrices | dimensionless (difference of Pearson r) | D1 > 0 and p_N1 < 0.05 (N1 on PRE and POST, 500 shuffles, seed 0), in each split | same cells in PRE, TASK, POST; at least 300 NREM frames in PRE and in POST |
| M2 explained variance vs. reverse | D2 = EV - REV, EV as in team brief section 4, REV with PRE and POST swapped | dimensionless (difference of squared partial correlations) | D2 > 0 in both splits A and B, and p_N1 < 0.05 in each split | as M1, plus at least two sessions; only two pseudo-sessions (splits A and B, same animal) exist, so a "yes" is reported with that caveat |
| M3 PCA reactivation strength | D3 = mean over significant TASK components k of (mean_t R_k(POST) - mean_t R_k(PRE)) | squared z-score per frame (dimensionless, a.u.) | D3 > 0 and p_N1 < 0.05 (500 shuffles, seed 0), in each split | at least one TASK eigenvalue above the N1 eigenvalue bound (95th percentile of the per-shuffle largest eigenvalue, 500 shuffles); at least 10 cells; TASK frames >= 5 x cells |
| M4 ICA reactivation strength | D4 = as D3, with ICA assembly patterns in place of PCA components | squared z-score per frame (dimensionless, a.u.) | D4 > 0 and p_N1 < 0.05 (500 shuffles, seed 0), in each split | as M3, but at least two significant components |

Method tests gate the keys: a method counts toward the overall verdict only if it passes its positive and negative controls on synthetic data (team brief section 2; proposed thresholds in [plans/engineer-b.md](plans/engineer-b.md) section 5).
With all 6,920 cells, "TASK frames >= 5 x cells" fails in both splits (fewer than 2,000 TASK frames each), so M3 and M4 need a cell selection rule, written here before signing.

### Overall verdict (DRAFT, owner Zixi)

Counted methods = eligible methods that passed their method tests.

- **Reactivation likely**: at least two counted methods say "yes" in both splits, and no counted method says "yes" in the reversed direction (POST and PRE swapped).
- **Reactivation not supported**: no counted method says "yes" in either split.
- **Not enough evidence**: anything else, including fewer than two counted methods.

The report also states the fraction of counted methods saying "yes" per split, as the "how likely" number (unit: methods / counted methods).

### Not decided yet (must be settled before signing)

Decided by the team lead (captain), 2026-11-07 15:45 CET, before any real-data result:

- TASK frames: **decided**, the full wake bout as in the vetting report (Split A frames 5481-7306, Split B frames 15006-15657, 0-based, half-open).
- Cell selection with 6,920 cells and fewer than 2,000 TASK frames per split: **decided**, the 300 most active cells by mean deconvolved activity (`spike`) over the union of both splits' TASK frames, so splits A and B use the same cells (needed for M2).
  The rule "TASK frames >= 5 x cells" is not changed: Split B (651 TASK frames) is therefore reported **not eligible** for M3 and M4, with the reason.
- Whether a supplementary block-swap null is required next to N1 for M3 and M4: **decided**, not required for the verdict; it may be reported as a supplementary column.

## Signature

The answer key above is locked before any result.

- Signed by (scientist):
- Date and time:
- Commit of this file at signing:
