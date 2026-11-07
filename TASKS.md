# Tasks

Prioritized loop task list.
Take the top open task, run READ -> PREDICT -> RUN (test first) -> JUDGE -> RECORD, log each step in [JOURNAL.md](JOURNAL.md), commit, then tick it here.
Owners: **A** = captain (Engineer A), **B** = colleague (Engineer B), **Zixi** = criterion and verdict.
Deadline 17:00.

## Gate

- [x] **T0** Scientist signs the answer key in [PROBLEM.md](PROBLEM.md); referee thresholds ([plans/engineer-b.md](plans/engineer-b.md) section 5) locked. Owner: Zixi with the scientist. No result is computed before this.
  Status: signed 2026-11-07 16:11 CET by Batu (team lead) on behalf of the team; no scientist sign-off was available. Signed after the first results. The answer key and all decisions were committed before any real-data result: commit 20a62a8 (15:44 CET, decisions); first PREDICT 15:47, first real result 15:48 (see JOURNAL.md). Nothing in the key was changed after a result.

## Loop tasks, in order

- [x] **Loop 3** rate confound (Tingley & Peyrache 2020, 3b-v) on DANDI:000044: r(log POST/PRE NREM rate, D3) = 0.136, p = 0.749, n = 8: not supported. See JOURNAL.md RECORD Loop 3.
- [x] **Loop 4** M3 bin-size robustness (Tingley & Peyrache 2020, 3b-v) on DANDI:000044, sessions Achilles_10252013, Achilles_11012013, Cicero_09102014 at 50/100/200 ms: yes in 9/9, robust. See JOURNAL.md RECORD Loop 4.

- [x] **T1 Loader** (A): `toolbox/loader.py` reads `sleep_data.mat` into `toolbox.contract.Recording` for Split A and Split B, `fs = 7.65`, stage mapping and splits as in [PROBLEM.md](PROBLEM.md).
  Done when `tests/test_loader.py` passes (frame counts per epoch equal the vetting report) and a missing required field stops with a clear message.
- [x] **T2 M1 cell-pair correlation** (A): `toolbox/m1_pair_corr.py`, key D1.
  Done when positive and negative controls pass on synthetic data and the result JSON for both splits is in `results/`.
  Real data (16:02): Split A D1 = -0.0691, p_N1 = 1.0; Split B D1 = +0.00608, p_N1 = 0.194. Referee cases a-d pass. See JOURNAL.md RECORD T2.
- [x] **T3 M3 PCA reactivation strength** (B): `toolbox/assemblies.py`, `toolbox/m3_pca.py`, key D3.
  Done when T-A1 to T-A5 and T-M3-1 to T-M3-8 pass.
  Real data (16:12): Split A D3 = -0.146, p_N1 = 1.0; Split B not eligible (TASK frames 651 < 1500). See JOURNAL.md RECORD T3/T6 real data.
- [x] **T4 N1 null model** (B): `toolbox/nulls.py` (offsets, circular shift, p-value, seeded streams) and the N1 eigenvalue bound.
  Real data (16:12): N1 eigenvalue bound 2.42 on Split A, n_sig 15, 500 shuffles.
  Done when T-N1-1 to T-N1-9 pass. M1 and M3 report `p_n1` only after this lands; build them against the `nulls.py` interface.
- [ ] **T5 M2 EV vs. REV** (A): `toolbox/m2_ev_rev.py`, key D2, across splits A and B.
  Done when controls pass and the two-pseudo-session caveat is in the result.
  Status (A, 15:50): implemented; caveat in every result. Controls: locked N1 rule fails pre_existing (6/10), N1 + block-swap fails positive (8/10); synthetic results only (loader not on main). Not ticked. See JOURNAL.md RECORD T5.
- [ ] **T6 M4 ICA reactivation strength** (B): `toolbox/m4_ica.py`, key D4.
  Status (B, 15:40): implemented; T-M4-2 to T-M4-4 pass, T-M4-1 fails at its locked threshold (PCA 0.817, needs < 0.8). Not ticked. See journal/engineer-b.md Entry 2.
  Real data (16:12): Split A D4 = -0.061, p_N1 = 1.0; Split B not eligible. Box stays open: T-M4-1 still fails. See JOURNAL.md RECORD T3/T6 real data.
  Done when T-M4-1 to T-M4-4 pass. Cut rule: if M3 is not done by 16:05, M4 is reported `eligible=False, reason="not implemented"`.
- [x] **T7 Verdict rule** (Zixi, draft): `toolbox/verdict.py` and `toolbox/controls.py` turn method results and control outcomes into the overall verdict defined in [PROBLEM.md](PROBLEM.md).
  Done when the rule has a test with hand-made `MethodResult` inputs covering all three outcomes.
- [x] **T8 One-command repro** (A): `python run.py --data <path to sleep_data.mat> --seed 0` writes every result file and the results table from a fresh clone.
  Done when a fresh clone reproduces byte-identical result JSON.
  Status (16:22): fresh clone of b11e8d0. `uv run --python 3.12 python run.py --data sleep_data.mat --seed 0` (61 s) wrote eight `mouse05_split{A,B}__M{1-4}.json` files, each byte-identical to `results/real/M{n}_split{A,B}.json`, plus `summary.csv`. Fast tests: 117 passed, 1 failed (T-M4-1, pre-existing), 2 xfailed, 20 deselected. See JOURNAL.md RECORD T8.
- [x] **Loop 2** M1 and M2 on the 8 DANDI:000044 sessions: M1 "yes" 6/8, M2 "yes" 7/8 (mean EV 0.088 > REV 0.025); both pass. See JOURNAL.md RECORD Loop 2.
- [ ] **T9 Submission issue** (A): open the project-submission issue on https://github.com/xemantic/claude-impact-lab-2026 with the repo link, license (Apache-2.0 code, CC BY 4.0 text), dataset citation and license, and the verdict.
  Done before 17:00.
