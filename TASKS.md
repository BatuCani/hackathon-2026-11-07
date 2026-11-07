# Tasks

Prioritized loop task list.
Take the top open task, run READ -> PREDICT -> RUN (test first) -> JUDGE -> RECORD, log each step in [JOURNAL.md](JOURNAL.md), commit, then tick it here.
Owners: **A** = captain (Engineer A), **B** = colleague (Engineer B), **Zixi** = criterion and verdict.
Deadline 17:00.

## Gate

- [ ] **T0** Scientist signs the answer key in [PROBLEM.md](PROBLEM.md); referee thresholds ([plans/engineer-b.md](plans/engineer-b.md) section 5) locked. Owner: Zixi with the scientist. No result is computed before this.

## Loop tasks, in order

- [x] **T1 Loader** (A): `toolbox/loader.py` reads `sleep_data.mat` into `toolbox.contract.Recording` for Split A and Split B, `fs = 7.65`, stage mapping and splits as in [PROBLEM.md](PROBLEM.md).
  Done when `tests/test_loader.py` passes (frame counts per epoch equal the vetting report) and a missing required field stops with a clear message.
- [ ] **T2 M1 cell-pair correlation** (A): `toolbox/m1_pair_corr.py`, key D1.
  Done when positive and negative controls pass on synthetic data and the result JSON for both splits is in `results/`.
- [x] **T3 M3 PCA reactivation strength** (B): `toolbox/assemblies.py`, `toolbox/m3_pca.py`, key D3.
  Done when T-A1 to T-A5 and T-M3-1 to T-M3-8 pass.
- [x] **T4 N1 null model** (B): `toolbox/nulls.py` (offsets, circular shift, p-value, seeded streams) and the N1 eigenvalue bound.
  Done when T-N1-1 to T-N1-9 pass. M1 and M3 report `p_n1` only after this lands; build them against the `nulls.py` interface.
- [ ] **T5 M2 EV vs. REV** (A): `toolbox/m2_ev_rev.py`, key D2, across splits A and B.
  Done when controls pass and the two-pseudo-session caveat is in the result.
  Status (A, 15:50): implemented; caveat in every result. Controls: locked N1 rule fails pre_existing (6/10), N1 + block-swap fails positive (8/10); synthetic results only (loader not on main). Not ticked. See JOURNAL.md RECORD T5.
- [ ] **T6 M4 ICA reactivation strength** (B): `toolbox/m4_ica.py`, key D4.
  Status (B, 15:40): implemented; T-M4-2 to T-M4-4 pass, T-M4-1 fails at its locked threshold (PCA 0.817, needs < 0.8). Not ticked. See journal/engineer-b.md Entry 2.
  Done when T-M4-1 to T-M4-4 pass. Cut rule: if M3 is not done by 16:05, M4 is reported `eligible=False, reason="not implemented"`.
- [ ] **T7 Verdict rule** (Zixi): `toolbox/verdict.py` and `toolbox/controls.py` turn method results and control outcomes into the overall verdict defined in [PROBLEM.md](PROBLEM.md).
  Done when the rule has a test with hand-made `MethodResult` inputs covering all three outcomes.
- [ ] **T8 One-command repro** (A): `python run.py --data <path to sleep_data.mat> --seed 0` writes every result file and the results table from a fresh clone.
  Done when a fresh clone reproduces byte-identical result JSON.
  Status (A, partial): `run.py` wired (loader, every method with `run()`, `results/real/*.json`, `summary.csv`), byte-identical on synthetic data (`tests/test_run.py`); not run on real data until T0 is signed; method tests and verdict not wired yet.
- [ ] **T9 Submission issue** (A): open the project-submission issue on https://github.com/xemantic/claude-impact-lab-2026 with the repo link, license (Apache-2.0 code, CC BY 4.0 text), dataset citation and license, and the verdict.
  Done before 17:00.
