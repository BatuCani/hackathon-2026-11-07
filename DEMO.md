# Demo script (3 minutes)

Follows the loop diagram [research/research-loop.png](research/research-loop.png) top to bottom.
Times are cumulative.
Show = what is on screen; Say = what the speaker says.
Numbers come from [results/real/](results/real/) and match [SUBMISSION.md](SUBMISSION.md).
Figures live in [results/figures/](results/figures/); if a figure named below is missing, show the result file next to it instead.

## 0:00-0:20 Who and what

Show: the repository front page.

Say:
"We are Shift Happens.
Our question: when a mouse sleeps after doing something, do its neurons replay the patterns from that waking time?
The open problem: those methods were built for sparse spikes, and nobody has checked whether they hold up on slow calcium data; the field's own review lists that as missing.
We built an open toolbox that runs the four standard reactivation methods on two-photon calcium data, and only lets a method vote if it first passes tests on data where we planted the answer."

## 0:20-0:50 Before the loop: question, answer key, referee

Show: [research/research-loop.png](research/research-loop.png), top half (boxes 1-3), then [PROBLEM.md](PROBLEM.md) answer-key table.
Then [results/figures/controls_m3_m4.png](results/figures/controls_m3_m4.png) (fraction of seeds saying yes per control case; dashed line 0.9 = pass for the positive case, dotted line 0.1 = pass for the negatives).

Say:
"Before any result we wrote the question in the scientist's words, then one number, one unit and one yes-threshold per method, all against the same null: each neuron's trace shifted by its own random offset, 500 times.
Then the referee: synthetic calcium sessions with planted truth, reactivation, pure noise, assemblies already present before the task, and a firing-rate confound.
A method that cannot tell those apart does not get a vote."

## 0:50-1:20 The loop

Show: diagram boxes 4-8, then [JOURNAL.md](JOURNAL.md) scrolled to "PREDICT T5 real data" and "RECORD T5 real data".
Optional, if time: [results/figures/null_distribution_example.png](results/figures/null_distribution_example.png) (what one p against N1 looks like).

Say:
"Every step is read, predict, run, judge, record.
The prediction is committed before the run, so we cannot fit it afterwards.
Here we predicted M2 would say yes in both splits; it said no, and the journal records that as contradicted.
Claude Code agents ran each task in parallel worktrees; the journal is append-only, failures included."

## 1:20-1:35 Synthetic finding: spike tests are too lenient for calcium

Show: [results/figures/eigenvalue_bounds.png](results/figures/eigenvalue_bounds.png) (TASK spectrum of pure calcium-like noise against both bounds: 14 eigenvalues above Marchenko-Pastur, 0 above N1).

Say:
"First finding, before touching real data.
The analytical Marchenko-Pastur bound, the standard way to count assemblies in spike data, finds false assemblies in 50 of 50 pure-noise calcium runs.
Our shuffle bound finds them in 2 of 50.
Calcium is slow, and that alone breaks the spike-era test."

## 1:35-1:45 Positive control on real data

Show: [results/figures/positive_control_vs_riken.png](results/figures/positive_control_vs_riken.png) (left: 8 DANDI sessions, all positive with a star; right: RIKEN Split A negative, Split B ineligible), else [results/real/dandi/summary.csv](results/real/dandi/summary.csv).

Say:
"Does the toolbox find reactivation where it is known to exist?
We ran M3 and M4 on DANDI:000044.
DANDI:000044 (rat CA1, electrophysiology) is used only as a positive control for the methods, not as a biological comparison to the RIKEN mouse cortex calcium data (species, region, modality and task all differ).
On all eight sessions, PCA reactivation strength is positive and at the smallest possible p, 0.002: the toolbox says yes where reactivation is known to be.
Cell-pair correlation agrees in 6 of 8 and explained variance in 7 of 8, and the score does not track a firing-rate change, r = 0.14, p = 0.75."

## 1:45-2:20 Real data, one sentence per method

Show: [results/figures/real_scores.png](results/figures/real_scores.png) (one bar per method and split; star = p_N1 < 0.05, cross = ineligible).

Say, one line each:

- **M1 cell-pair correlation:** "The simplest method, cell-pair correlation, passes all four referee cases, and finds TASK pairs closer to sleep before than after in Split A, D1 = -0.069, p = 1.0; Split B is flat, +0.006, p = 0.19."
- **M2 explained variance vs. reverse:** "Split A points the wrong way, D2 = -0.026; Split B's tiny +0.002 is significant only against a null that M2 already fails on synthetic data, so M2 does not vote."
- **M3 PCA:** "Fifteen real assemblies, but they are stronger in sleep before the wake bout than after, D3 = -0.146, p = 1.0; Split B is too short to score."
- **M4 ICA:** "Same direction, D4 = -0.061, p = 1.0, and ICA failed one of its own tests, so it does not vote."

## 2:20-2:40 Verdict

Show: stay on [results/figures/real_scores.png](results/figures/real_scores.png), then [results/real/summary.md](results/real/summary.md) (the verdict the code wrote: not enough evidence, counted M1, 0/2 in Split A, 0/1 in Split B).

Say:
"The verdict rule needs at least two methods that are eligible and pass their tests.
Only cell-pair correlation is eligible and tested in both splits, so the verdict is: not enough evidence, and no counted method says yes in either split.
The patterns are real in sleep, but not specific to sleep after waking, which is what you expect: this recording has no task, so nothing was learned."

## 2:40-3:00 Where it got stuck, what next, how to run

Show: [SUBMISSION.md](SUBMISSION.md) "Where it got stuck", then "How to run it".

Say:
"Where we got stuck: one public session, no real task, M2 and M4 failing their own tests, and a short second split.
We kept every failure as a failure and moved no threshold.
Next: sessions with a real learning task, several animals, and a null that fixes M2.
Clone, download one zip from Zenodo, and the commands in How to run it give every number we just showed: run.py for the calcium results, scripts/run_dandi.py for the positive control."
