# Referee figures

Command, from the repository root:

```bash
uv run --python 3.12 --with matplotlib python scripts/plot_referee.py
```

The script uses NumPy seed 0 and pins BLAS to one thread.
It reads `results/engineer-b/*__R.npz` when a file already contains PRE, TASK and POST, and it reads `results/real/*.json` for the real-data bar.
Everything else is recomputed from the toolbox.
On this tree the engineer-b traces are absent, so the synthetic panels are recomputed (20 seeds, 100 N1 shuffles; the eigenvalue panel uses 200 shuffles).
The run takes about 90 seconds.

## eigenvalue_bounds.png

TASK eigenvalue spectrum of synthetic calcium-like noise (`tau_s = 1` s, no assemblies, seed 0) against the Marchenko-Pastur bound and the N1 bound.
Marchenko-Pastur flags false components (14 eigenvalues above it).
N1 does not (0 above it).
This is the T-N1-8 comparison.

## controls_m3_m4.png

Fraction of seeds on which M3 and M4 say yes, for the positive control and five negative controls.
Yes means eligible, score > 0, `p_N1 < 0.05` and `p_block-swap < 0.05`.
The dashed line at 0.9 is the pass for the positive case.
The dotted line at 0.1 is the pass for every other case.
In this run the positive control is 0.95 for both methods.
No-sleep co-activity is 0.15, just above the 0.1 line.
Pre-existing is 0.10, other assemblies is 0.00 for M3 and 0.05 for M4, and noise-only and reversal are 0.

## reactivation_strength_example.png

R(t) for the positive control in PRE, TASK and POST, seed 0.
Each panel shows the component traces and their mean, with a dashed line at the unsmoothed epoch mean.
The displayed traces use a 5 s moving average, and the y-axis is zoomed to that mean.
The unsmoothed means are PRE 0.105, TASK 1.284, POST 0.261 (POST - PRE = 0.156 a.u.), so mean reactivation strength is higher after the task than before it.

## null_distribution_example.png

N1 null distribution of the M3 score on the same positive-control seed.
The observed score (0.156) and its one-sided p-value (0.010) are marked.
The observed score sits above the null.

## real_scores.png

Drawn by `plot_real_results(results_dir)` when `results/real/*.json` contains method results (verdict files without a score are skipped).
One bar per method and split.
A star marks `p_N1 < 0.05`.
`n.s.` marks an eligible score that is not significant.
A cross marks an ineligible method, which has no score.
On the current real session the only significant positive score is M2 on split B (0.002).
M3 and M4 on split B are ineligible.
The other eligible scores are negative and not significant.
