# Engineer B plan: null model N1, M3 (PCA) and M4 (ICA) reactivation strength

As of 2026-11-07, 14:35 CET.
Written for Engineer B of the team brief.
Every instruction cites the repo file and section it comes from.
Files on open PRs are referenced by path:
`research/briefing.md` and `research/research-loop.png` (https://github.com/BatuCani/shift-happens/pull/1),
`research/source-of-truth.md` (https://github.com/BatuCani/shift-happens/pull/2),
`research/team-brief.md` and `research/findings/*.md` (https://github.com/BatuCani/shift-happens/pull/3).
`research/BUILD_APPROACH.md` and `research/README.md` are on main.

Labels used below:
- **[brief]**: fixed by `research/team-brief.md`; do not change without the team.
- **[SoT]**: from `research/source-of-truth.md` (the paper).
- **[TEAM DECISION]**: the repo leaves it open (mostly the source-of-truth list "What is not in the paper"); a recommended default is given, to be confirmed by Zixi or the scientist.
- **[PROPOSAL]**: a test threshold proposed for the referee to lock. None of them is calibrated. A small unrecorded planning pre-check (40 seeds, not in the repo, not a finding) informed some numbers; the tests must reproduce them before they count.

## 0. Method ID collision: read first

The team brief and the source of truth number methods differently.

| Team brief ID (`research/team-brief.md` §4) | Source-of-truth ID (`research/source-of-truth.md`) |
|---|---|
| M3 PCA reactivation strength | M4 (PCA per-component projectors), with M5 (number of significant components) |
| M4 ICA reactivation strength | M6 (ICA assembly patterns), with M5 |
| (not a team method) | M3 (projection onto the full correlation matrix) |

This plan uses the **team brief IDs** in code, files and results.
When citing the paper, it writes "SoT M4" etc.
[TEAM DECISION] Recommended: keep team-brief IDs everywhere and add this table to the results README.

## 1. Goal and scope

Goal of Engineer B, per `research/team-brief.md` §3 ("0:30 onwards") and §4 ("Null model N1 (Engineer B)"):

1. **N1 null model** [brief]: shift each neuron's trace by its own random circular offset, 500 times; this keeps each neuron's autocorrelation and breaks co-activity.
   Every method, including Engineer A's M1 and M2, reports p against N1, so B ships N1 first as a shared module.
2. **N1 eigenvalue bound** [brief]: significant components for M3 and M4 are those above the N1 eigenvalue bound, not the analytical (Marchenko-Pastur) bound, "because calcium bins are not independent".
3. **M3 PCA reactivation strength** [brief]: "yes" means mean strength in POST > PRE; needs at least one significant TASK component.
4. **M4 ICA reactivation strength** [brief]: as M3; needs at least two significant components.
5. Method-test hooks (positive and negative controls on synthetic data) that Zixi's verdict rule calls (`research/team-brief.md` §2 diagram: "Method tests, positive / negative controls", "counts only if tests pass").

Out of scope:
- Replay methods and M5-M8 of the team brief's requirement check: "Replay methods are out of scope: the requirements (fine timing, long sequences) do not hold for calcium data" (`research/team-brief.md` §4); the diagram routes them to "Ineligible methods, e.g. replay, M5-M8" (§2).
- The loader, M1 and M2 (Engineer A), and the final yes/no criterion and verdict rule (Zixi) (`research/team-brief.md` §3).
- Everything in `research/BUILD_APPROACH.md` about place fields, decoding and replay scores: that plan was written for replay; `research/findings/oss-toolboxes.md` says so in its note.
- Porting `RnR_methods` (`ReactStrength`): GPL-3.0; implement from the equations only (`research/team-brief.md` §5, `research/papers/README.md`). Do not open its source.

## 2. Shared contracts

### 2.1 Data contract with Engineer A

Fields come from the loader table in `research/team-brief.md` §4 ("What the loader imports automatically").
Field names are fixed [brief]; dtypes and shapes are [TEAM DECISION] proposals.

```python
SleepStage  = Literal["wake", "NREM", "REM", "unscored"]          # [brief] values
Epoch       = Literal["PRE", "TASK", "POST", "none"]              # derived by loader [brief]
SessionType = Literal["baseline", "training", "test", "spontaneous"]  # [brief] values

@dataclass(frozen=True)
class StimFrames:                    # [brief] "Onset, offset and identity of each stimulus"
    onset:   np.ndarray              # int64, (n_stim,), frame index, inclusive
    offset:  np.ndarray              # int64, (n_stim,), frame index, exclusive
    stim_id: np.ndarray              # str, (n_stim,)

@dataclass(frozen=True)
class Recording:
    deconv:       np.ndarray         # float64, (n_cells, n_frames); raw deconvolved, never smoothed [brief]
    sleep_stage:  np.ndarray         # str '<U8', (n_frames,), SleepStage values
    epoch:        np.ndarray         # str '<U4', (n_frames,), Epoch values; loader derives it [brief]
    fs:           float              # frame rate, Hz
    cell_id:      np.ndarray         # str, (n_cells,); same cells in PRE, TASK, POST [brief M1 "same cells"]
    mouse_id:     str
    session_id:   str
    session_type: SessionType        # metadata only for B; see open question Q4
    stim_frames:  StimFrames | None  # required "if a task exists" [brief]

def analysis_mask(rec: Recording, epoch: Literal["PRE", "TASK", "POST"]) -> np.ndarray: ...
    # bool (n_frames,). The single definition of which frames a method sees.
    # PRE  -> epoch == "PRE"  & sleep_stage == "NREM"   [brief: "PRE and POST use NREM frames only"]
    # POST -> epoch == "POST" & sleep_stage == "NREM"   [brief]
    # TASK -> epoch == "TASK" & sleep_stage != "unscored"   [TEAM DECISION, see Q5]
```

Missing required field: the loader stops "with a clear message" [brief §4]; B's methods assume a valid `Recording` and only check numeric preconditions (finite values, shapes).
Fallback dataset (RIKEN cortex, "a wake bout between two sleep bouts standing in for TASK", `research/team-brief.md` §3) needs no contract change: the loader labels that wake bout `TASK`.

### 2.2 Return contract (every method, M1-M4)

The brief requires that every method reports p against N1 (§4) and that ineligible methods list missing data (§2 diagram).

```python
@dataclass(frozen=True)
class Requirement:
    eligible: bool
    reason:   str                    # "" if eligible; else the first failed requirement, with numbers
    missing:  tuple[str, ...]        # data the method would need, e.g. ("POST NREM frames >= 300",)

@dataclass(frozen=True)
class MethodResult:
    method_id:  str                  # "M1".."M4", team-brief IDs
    session_id: str
    eligible:   bool
    reason:     str
    score:      float                # nan if not eligible; M3/M4: see 4.4
    p_n1:       float                # nan if not eligible; one-sided p against N1
    n_shuffles: int                  # 500 [brief]
    seed:       int
    params:     dict                 # every parameter used, for the results file
    details:    dict                 # method-specific: n_sig, eigenvalues, bounds, per-component deltas
    missing:    tuple[str, ...] = ()

    def to_json(self) -> str: ...    # nan -> null, sort_keys=True, so equal results give equal bytes

# Every method module exposes exactly:
def check_requirements(rec: Recording, params) -> Requirement: ...
def run(rec: Recording, *, seed: int, params=None) -> MethodResult: ...
```

B does not decide "yes": Zixi's rule turns `score`, `p_n1` and `eligible` into the verdict (`research/team-brief.md` §3).

## 3. File layout and ownership

No file has two owners.
`contract.py` and `pyproject.toml` are shared: one bootstrap PR, then frozen; changes only by a PR both engineers approve.

```text
pyproject.toml                       bootstrap (owner A), frozen after merge
src/reactivation/__init__.py         bootstrap, empty
src/reactivation/contract.py         bootstrap: sections 2.1 and 2.2 verbatim
src/reactivation/loader.py           A
src/reactivation/m1_pair_corr.py     A
src/reactivation/m2_ev_rev.py        A
src/reactivation/nulls.py            B   N1 offsets, shift, p-value, seeded streams (A imports, read-only)
src/reactivation/assemblies.py       B   z-score, correlation, eigen, projectors, R(t), N1 eigen bound
src/reactivation/m3_pca.py           B
src/reactivation/m4_ica.py           B
src/reactivation/synth.py            B   synthetic calcium-like Recording (A may import for M1/M2 tests)
src/reactivation/controls.py         B   positive/negative control runs for the method tests
src/reactivation/verdict.py          Zixi
tests/test_loader.py, test_m1.py, test_m2.py                                   A
tests/test_synth.py, test_n1.py, test_assemblies.py, test_m3.py, test_m4.py    B
tests/test_crosscheck_neurospatial.py                                          B, optional
scripts/run_b.py                     B   M3/M4 on all sessions -> results/engineer-b/
results/engineer-b/                  B   generated only, never hand-edited
journal/engineer-b.md                B   append-only notebook
```

Package name `reactivation`, Python 3.12 with `uv` (the version measured in `research/findings/oss-toolboxes.md`), dependencies numpy, scipy, scikit-learn, pytest: [TEAM DECISION].
scikit-learn is BSD-3 and already a core dependency of neurospatial (`research/findings/oss-toolboxes.md`), so it fits the lab's Apache-2.0 rule (`research/briefing.md` §3).

## 4. Step-by-step tasks, 14:40 to 17:00

Deadline 17:00, 3-minute demo (`research/team-brief.md` §3 "Last 30 min"; `research/briefing.md` §3 agenda).
Priority if behind: N1 > M3 > M4 > cross-check.
Cut rules: N1 not merged by 15:35 means stop everything else and fix it, because A needs it too; M3 not done by 16:05 means M4 is reported as `eligible=False, reason="not implemented"`, honestly.

### Step 0 (14:40-14:50): sync

Settle the open questions in section 9 with A and Zixi.
Done-check: answers written as the first entry in `journal/engineer-b.md`; contract PR opened.

### Step 1 (14:50-15:05): synthetic calcium-like data and tests skeleton

```python
def make_session(*, n_cells=50, fs=10.0,
                 frames={"PRE": 5700, "TASK": 6000, "POST": 5700},
                 nrem_fraction=0.7,
                 assemblies: Sequence[np.ndarray] = (),      # member cell indices per assembly
                 p_activation={"PRE": 0.0, "TASK": 0.02, "POST": 0.005},  # per frame, per assembly
                 p_member=0.8, tau_s=0.0, seed=0,
                 session_id="synth") -> Recording: ...
```

Pseudocode:
- Background: per-cell rate lognormal (the paper notes lognormal rates, `research/source-of-truth.md` A40), events Bernoulli(rate/fs) per frame, amplitudes lognormal(0, 0.5).
- Assemblies: per frame and assembly, activation Bernoulli(p_activation[epoch]); when active each member fires with probability p_member.
- Calcium-like stress: if `tau_s > 0`, AR(1) filter with a = exp(-1/(tau_s * fs)) per cell. This is the autocorrelation the brief warns about (§1 "Why it is hard"), used only to stress the null; real `deconv` is never smoothed [brief].
- Sleep stages: PRE and POST as alternating NREM/REM/wake bouts with the requested NREM fraction; TASK all `wake`. Assemblies are active only on NREM frames in PRE/POST.

Done-check: T-S1 to T-S3 pass.

### Step 2 (15:05-15:35): N1 null model (`nulls.py`) and N1 eigenvalue bound

```python
def rng_for(seed: int, session_id: str, purpose: str) -> np.random.Generator: ...
    # np.random.default_rng([seed, zlib.crc32(session_id.encode()), zlib.crc32(purpose.encode())])
    # never Python hash(): it is randomised per process
def n1_offsets(n_cells: int, n_frames: int, n_shuffles: int, rng, min_shift: int = 1) -> np.ndarray: ...
    # int64 (n_shuffles, n_cells), uniform on [min_shift, n_frames - min_shift]
def circular_shift(X: np.ndarray, offsets: np.ndarray) -> np.ndarray: ...
    # row i rolled by offsets[i]; idx = (arange(B) - offsets[:, None]) % B; take_along_axis
def n1_surrogates(X: np.ndarray, n_shuffles: int, rng, min_shift: int = 1) -> Iterator[np.ndarray]: ...
def n1_pvalue(observed: float, null: np.ndarray) -> float: ...
    # one-sided "greater": (1 + #{null >= observed}) / (1 + len(null)); minimum 1/501 for 500 shuffles
```

In `assemblies.py`:

```python
@dataclass(frozen=True)
class EigenBound:
    bound: float                     # N1 bound
    null_max_eigs: np.ndarray        # (n_shuffles,), largest eigenvalue per shuffle
    mp_bound: float                  # analytical bound, reported for comparison only
    quantile: float

def n1_eigen_bound(Z_task: np.ndarray, *, n_shuffles=500, quantile=0.95, rng) -> EigenBound: ...
    # for each shuffle: Zs = circular_shift(Z_task, offsets); C = Zs Zs^T / B; eigvalsh(C)[-1]
    # bound = quantile of the per-shuffle maxima
```

Math and parameters:
- 500 shuffles, own offset per neuron [brief §4].
- Shift the concatenated analysis matrix (the frames the method sees, after `analysis_mask`), not the full recording; shifting the full epoch would move wake frames into NREM frames and change each cell's value distribution. [TEAM DECISION]
- Offsets uniform on [1, B-1] (`min_shift=1`), the literal reading of "random circular offset". [TEAM DECISION] Sensitivity variant: `min_shift = ceil(0.1 * B)`.
- Bound = 95th percentile of the per-shuffle largest eigenvalue. The paper gives no shuffle count or percentile (`research/source-of-truth.md` M5 "Shuffle count and percentile: not stated"; "What is not in the paper" item 2). [TEAM DECISION]
- The paper calls the shuffle null and the Marchenko-Pastur bound "equivalent" for independent bins (`research/source-of-truth.md` M5); the analytical formula is not in the paper (item 1). `research/briefing.md` §2 gives the standard random-matrix form lambda_max = (1 + sqrt(N/B))^2, marked "not verbatim". Report it as `mp_bound` for comparison only, never for selection [brief].
- Circular shift preserves each row's values, so z-score once and shift the z-scored matrix.

Edge cases:
- B < 2 * min_shift + 1: raise ValueError with the numbers.
- Zero-variance row: cannot be z-scored; drop before (see Step 3).
- Cost: one shuffle costs N^2 B for the correlation matrix. For N = 500, B = 18000 that is about 4.5e9 flops per shuffle; time it on the real session first; if 500 shuffles exceed 2 minutes, note it in the journal, do not silently lower the count.

Done-check: T-N1-1 to T-N1-9 pass; PR merged; A told the import path.

### Step 3 (15:35-16:05): M3 PCA reactivation strength (`assemblies.py`, `m3_pca.py`)

```python
@dataclass(frozen=True)
class AssemblyParams:
    n_shuffles: int = 500              # [brief]
    bound_quantile: float = 0.95       # [TEAM DECISION], SoT gap 2
    min_shift: int = 1                 # [TEAM DECISION]
    bin_frames: int = 1                # [TEAM DECISION], SoT gap 5
    min_cells: int = 10                # [TEAM DECISION], SoT gap 7
    min_task_frames_per_cell: int = 5  # [TEAM DECISION]: B_task >= 5 * N
    min_sleep_frames: int = 300        # [TEAM DECISION]: per PRE and POST NREM
    ddof: int = 0                      # SoT shared preprocessing: 1/B form

def zscore(X: np.ndarray, ddof: int = 0) -> np.ndarray: ...
def correlation(Z: np.ndarray) -> np.ndarray: ...        # C = Z Z^T / B, (N, N)
def eigh_desc(C: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...
def projector(v: np.ndarray) -> np.ndarray: ...          # P = v v^T with diag set to 0
def reactivation_strength(V: np.ndarray, Z: np.ndarray) -> np.ndarray: ...
    # (K, B): R_k(t) = (v_k . z(t))^2 - sum_i v_ki^2 z_i(t)^2   == z^T P_k z with zero diagonal
def mean_strength(V: np.ndarray, Z: np.ndarray) -> np.ndarray: ...
    # (K,): v_k^T C_Z v_k - ||v_k||^2   (closed form of the time average, needs ddof=0)

@dataclass(frozen=True)
class Subspace:
    kept_cells: np.ndarray; dropped_cells: np.ndarray
    eigvals: np.ndarray; V_sig: np.ndarray; n_sig: int; bound: EigenBound
    Z: dict[str, np.ndarray]           # "PRE", "TASK", "POST" z-scored analysis matrices

def significant_subspace(rec: Recording, params: AssemblyParams, seed: int) -> Subspace | Requirement: ...
    # shared by M3 and M4, same rng stream "eigen_bound", so both agree on n_sig
```

Math (all from `research/team-brief.md` §4 and `research/source-of-truth.md`):
1. Select frames with `analysis_mask` for PRE, TASK, POST; same kept cells in all three.
2. Z-score each epoch separately ("during each epoch", SoT "Shared preprocessing"), population sd (ddof=0, matches the 1/B form).
3. TASK correlation matrix C = Z Z^T / B (N x N). The SoT writes Z^T Z; that is a flagged notational issue (SoT "Notes on the formula"); the intended object is N x N.
4. Eigen-decomposition C v_i = lambda_i v_i, C = sum_i lambda_i v_i v_i^T (SoT M4).
5. Significant components: lambda_i > N1 bound [brief].
6. Projector P_k = v_k v_k^T with diagonal 0 (SoT A06; team brief §4).
7. R_k(t) = z(t)^T P_k z(t) on PRE-NREM and POST-NREM frames (team brief §4; SoT M4 expansion sum over k != l).
8. Per component: delta_k = mean_t R_k(POST) - mean_t R_k(PRE).
9. Session score: score = mean over significant k of delta_k. [TEAM DECISION] Alternatives: sum, or per-component tests.
10. p_n1: for each of 500 shuffles, apply N1 independently to Z_PRE and Z_POST (templates from real TASK stay fixed), recompute the score; p = (1 + #{null >= score}) / 501.

Eligibility (requirement check): N_kept >= 10, B_task >= 5 N, PRE and POST NREM frames >= 300 each, all finite, n_sig >= 1 [brief: "At least one significant TASK compo[nent]"; the brief's cell is cut off at the screenshot edge, `research/team-brief.md` §4].

Edge cases:
- Zero-variance cell in any of the three analysis matrices: drop it from all epochs, list it in `details["dropped_cells"]`. [TEAM DECISION], SoT gap 4.
- Too few NREM frames: `eligible=False`, reason with the numbers, `missing=("POST NREM frames >= 300",)`.
- n_sig = 0: `eligible=False`, reason "0 TASK components above N1 bound (lambda_1=..., bound=...)".
- Near-equal eigenvalues (equal-size assemblies): PCs can be rotations of the assemblies (the orthogonality failure mode, SoT M4 §2d). Scores stay valid; do not interpret individual PC weights.
- Rebinning (`bin_frames > 1`): sum within contiguous runs of the mask only, drop remainders; the paper's reactivation bins are about 50-200 ms (SoT A41), so at 30 Hz the sweep is 1, 3, 6 frames. Default 1. Only if time.

Known limitation found while planning, to verify by test T-M3-3: the N1 null for the POST minus PRE difference keeps only noise variance.
When assemblies are equally present in PRE and POST, the sampling variance of their activation counts is missing from the null, so p_n1 is anticonservative (planning pre-check: 7/40 seeds with p < 0.05 at nominal 5%).
A supplementary block-swap null (cut PRE and POST NREM R(t) into 20 s blocks, reassign blocks to PRE/POST labels 500 times) gave 3/40 in the same pre-check.
[TEAM DECISION for Zixi] Recommended: report `details["p_blockswap"]` next to `p_n1` and let the verdict rule require both.

`details` to report: top-10 eigenvalues, bound, mp_bound, n_sig, delta_k, mean R PRE and POST per component, p_n1 for POST alone and PRE alone, p_blockswap, dropped cells, and an `.npz` of R(t) for the demo plot (SoT §2b "Tracking reactivation over time").

Done-check: T-A1 to T-A5 and T-M3-1 to T-M3-8 pass; one synthetic result JSON in `results/engineer-b/`.

### Step 4 (16:05-16:25): M4 ICA reactivation strength (`m4_ica.py`)

```python
@dataclass(frozen=True)
class ICAParams:
    fun: str = "logcosh"; whiten: str = "unit-variance"
    max_iter: int = 1000; tol: float = 1e-4        # all [TEAM DECISION], SoT gap 3

def ica_weights(sub: Subspace, params: ICAParams, rng) -> np.ndarray: ...   # (N, n_sig), unit columns
def run(rec: Recording, *, seed: int, params=None) -> MethodResult: ...
```

Math: "ICA is performed on the data projected onto the subspace of the significant components ... to de-mix the PCs into independent components" (SoT M6, §2e); the IC projectors replace the PC projectors (SoT M6, figure 2 caption).
Pseudocode:
- Y = V_sig^T Z_TASK, shape (n_sig, B).
- FastICA (scikit-learn) with n_components = n_sig, random_state from `rng_for(seed, session_id, "ica")`, fit on Y^T.
- Weights W = V_sig @ components_.T, shape (N, n_sig); normalise each column to unit norm; sign so the largest-|w| entry is positive.
- Then exactly Step 3 items 6-10 with W in place of V_sig.

Eligibility: as M3, plus n_sig >= 2 [brief: "At least two significant components"; the cell may continue past the screenshot edge, `research/team-brief.md` §4].
Edge cases: FastICA ConvergenceWarning: retry once with max_iter 5000; still not converged: `eligible=False`, reason "ICA did not converge". [TEAM DECISION]
Done-check: T-M4-1 to T-M4-4 pass.

### Step 5 (16:25-16:30): real data run

`scripts/run_b.py --seed 0` loads every session with A's loader, runs M3 and M4, writes `results/engineer-b/<session_id>__<method>.json`, `R(t)` `.npz` and `summary.csv` (columns: session_id, method_id, eligible, reason, score, p_n1, p_blockswap, n_sig, n_shuffles, seed, git_sha).
If the loader is not merged by 16:25, run on synthetic sessions only and say so in the journal.

### Step 6 (16:30-17:00): put it together

Per `research/team-brief.md` §3 "Last 30 min": all methods on all sessions, Zixi's criterion, one results table, the demo following the diagram.
B delivers results and control runs and answers method questions; no new features.
Before 17:00: fresh clone, one command (`research/research-loop.png` "5 SHIP", "11 REPRO + SUBMIT").

## 5. Tests to write first ([PROPOSAL], for the referee to lock)

Written before the implementation (`research/research-loop.png` "3 REFEREE: right answer passes, wrong answer fails; locked before any result").
Default synthetic setting: N = 50, fs = 10 Hz, TASK 6000 frames, PRE/POST about 4000 NREM frames, K = 3 assemblies of 8 cells (cells 0-23), p_activation TASK 0.02.
Counted tests use 50 seeds and 200 shuffles (`@pytest.mark.slow`); the default fast run uses 10 seeds with "at least 9/10" and "at most 2/10".
None of the numbers is calibrated.

| ID | Test | Pass threshold |
|---|---|---|
| T-S1 | `make_session` matches the contract: dtypes, shapes, labels; NREM fraction | within 0.02 of requested |
| T-S2 | Determinism | same seed gives `np.array_equal`; different seed differs |
| T-S3 | Autocorrelation | tau_s = 1: lag-1 autocorrelation >= 0.8 (theory a = 0.905); tau_s = 0: below 0.05 in absolute value |
| T-N1-1 | Shift keeps each row's values | `np.sort(Xs, 1) == np.sort(X, 1)` exactly |
| T-N1-2 | Shift keeps autocorrelation | circular autocorrelation per row equal to 1e-12 |
| T-N1-3 | Offsets | int64, shape (n_shuffles, n_cells), all in [min_shift, B - min_shift] |
| T-N1-4 | Co-activity broken | tau_s = 0, planted: mean member-pair correlation after one shift below 0.01 in absolute value |
| T-N1-5 | Seeds | same (seed, session, purpose) gives identical offsets; other purpose differs |
| T-N1-6 | p-value | observed above all 500: p = 1/501; below all: p = 1.0; ties count as >= |
| T-N1-7 | Bound equals analytical bound for independent bins | K = 0, tau_s = 0: bound within 0.02 of (1 + sqrt(50/6000))^2 = 1.191 (pre-check mean 1.194) |
| T-N1-8 | Brief's claim: analytical bound too lenient for calcium | K = 0, tau_s = 1: N1 gives >= 1 component in at most 5/50 seeds; MP gives >= 5 false components in at least 45/50 (pre-check: N1 1/20, MP 11-14 per seed) |
| T-N1-9 | Planted recovery | K = 3, tau_s in {0, 1}: n_sig == 3 in at least 47/50 (pre-check 20/20) |
| T-A1 | Hand example | 4 cells: R equals the explicit sum over k != l of v_k v_l z_k z_l to 1e-12 (SoT M4) |
| T-A2 | Closed form | mean_t R_k equals v^T C v - 1 to 1e-10 |
| T-A3 | Rate invariance | per-cell a_i x + b_i with a_i > 0 leaves R unchanged to 1e-10 |
| T-A4 | Correlation | `correlation(zscore(X))` equals `np.corrcoef(X)` to 1e-12 |
| T-A5 | Zero-variance cell | dropped and listed, method still runs |
| T-M3-1 | Positive control | PRE 0, POST 0.005, tau_s = 1: score > 0 and p_n1 < 0.05 in at least 47/50 (pre-check 40/40) |
| T-M3-2 | Negative: no sleep co-activity | PRE = POST = 0: p_n1 < 0.05 in at most 5/50 (pre-check 2/40) |
| T-M3-3 | Negative: pre-existing | PRE = POST = 0.005: p_blockswap < 0.05 in at most 5/50; p_n1 rate reported, not gated (pre-check 7/40) |
| T-M3-4 | Negative: other assemblies | POST assemblies on cells 24-47: p_n1 < 0.05 in at most 5/50 |
| T-M3-5 | Noise only | TASK K = 0, tau_s = 1: `eligible=False` in at least 45/50, reason names the N1 bound |
| T-M3-6 | Ineligibility | 5 cells; 0 POST NREM frames; NaN in deconv: each `eligible=False` with the matching reason |
| T-M3-7 | Determinism | two runs, same seed: identical `to_json()` bytes |
| T-M3-8 | Reversal | PRE and POST swapped in T-M3-1: score < 0 and p_n1 > 0.95 in at least 47/50 |
| T-M4-1 | Overlap (SoT A13; `research/briefing.md` §5B) | 50% member overlap: matched mean absolute cosine ICA >= 0.9, PCA < 0.8 (Hungarian matching) |
| T-M4-2 | Controls | T-M3-1 to T-M3-5 repeated for M4, same thresholds |
| T-M4-3 | Requirement | n_sig = 1: `eligible=False`, reason "1 < 2 significant components" |
| T-M4-4 | Determinism and sign | same seed: identical weights; largest-|w| entry positive |

## 6. How B's outputs feed Zixi's verdict rule

- Input to the rule: one `MethodResult` per session and method, as JSON in `results/engineer-b/` plus `summary.csv`.
- Requirement check (`research/team-brief.md` §2 "Requirement check per method"): B computes `eligible` for M3 (n_sig >= 1) and M4 (n_sig >= 2) plus the data minima in Step 3. n_sig needs the N1 eigen bound, so the check runs that part; M3 and M4 share it through `significant_subspace`.
- Ineligible: `reason` and `missing` go to the report ("missing data listed", diagram).
- Eligible: `score > 0` is the direction ("Mean strength in POST > PRE" [brief]); `p_n1` (and `p_blockswap` if adopted) is the evidence. The threshold alpha (recommended 0.05) and the cross-session rule are Zixi's.
- "No, or methods disagree" goes to method tests (diagram). B provides:

```python
def run_controls(method_id: str, like: Recording, *, seed: int, n_seeds: int = 20) -> ControlReport: ...
    # synthetic sessions matched to `like`: n_cells, frames per epoch, fs, median lag-1 autocorrelation
    # positive: planted reactivation; negatives: T-M3-2, -3, -4 scenarios
@dataclass(frozen=True)
class ControlReport:
    method_id: str; tpr: float; fpr: dict[str, float]; passed: bool; thresholds: dict
```

## 7. Optional cross-check against neurospatial

Only if M3 and M4 are merged before 16:25; otherwise journal it as not done.
Source: `research/findings/tool-fit.md` (neurospatial as an independent reference, not a dependency) and `research/findings/oss-toolboxes.md` (MIT, pin `0cc33ecd374fd56270b0618aaf82eae5a030da61`; `reactivation/__init__.py:8-16` `detect_assemblies` (ICA/PCA/NMF) and `assembly_reactivation`; PyPI 0.6.0 lacks `reactivation`).

- Run in a throwaway environment: `uv run --no-project --python 3.12 --with "neurospatial @ git+https://github.com/edeno/neurospatial@0cc33ecd374fd56270b0618aaf82eae5a030da61" ...`; do not add it to `pyproject.toml`.
- Read the real signatures at the pin first (`inspect.signature`); `research/findings/tool-fit.md` says it is unverified whether it accepts deconvolved calcium matrices.
- Feed both the same z-scored TASK matrix and force the same component count.
- Must agree: PCA weights up to sign (absolute cosine >= 0.99 per component); R(t) on PRE and POST (Pearson >= 0.99); ICA weights after Hungarian matching (mean absolute cosine >= 0.9). [PROPOSAL]
- Expected to differ: the component count, if neurospatial uses an analytical bound; that difference is the brief's point, not a bug.

## 8. Git workflow and notebook

- Base every branch on main. Branches: `eng-b/synth`, `eng-b/n1`, `eng-b/m3`, `eng-b/m4`, `eng-b/run-results`, `eng-b/crosscheck`.
- One task per PR, small; A reviews B's PRs and B reviews A's within 5 minutes. Merge authority: [TEAM DECISION].
- Commit order per task: tests first (`test(n1): ...`), then implementation (`feat(n1): ...`), then journal and results (`docs(journal): ...`), so the history shows test-first ("a commit per task", "test-first", `research/briefing.md` §3 on the lab's RESEARCH-LOOPS.md).
- `journal/engineer-b.md`, append-only ("pen, no eraser. Every step writes here, failures too", `research/research-loop.png`). One entry per loop step: time; READ (source and quote); PREDICT (written and committed before the run); RUN (command, seed, git SHA); JUDGE (which test decided); RECORD (result file path and label: verified, contradicted or not enough evidence).
- Findings only as numbers with a file ("10 FINDINGS: only numbers with a file", `research/research-loop.png`); the jury checks every claim against repo files (`research/briefing.md` §3).
- Results are generated by `scripts/run_b.py`, never edited by hand.

## 9. Open questions for the first 10 minutes

1. Method IDs: team-brief numbering in code (section 0)? (A, Zixi)
2. Who writes the bootstrap PR (`pyproject.toml`, `contract.py`), and is section 2 accepted as is? (A)
3. Which dataset was chosen at 0:30; fs, cell count, frames per epoch? This decides whether 500 shuffles fit in time. (A)
4. Is `session_type` per session or per segment? (A)
5. TASK frames: all non-unscored TASK frames, or wake only? (Zixi)
6. Score aggregation across components (mean of deltas) and alpha = 0.05? (Zixi)
7. N1 details: shift the NREM-only concatenated matrix; offsets on [1, B-1]; bound at the 95th percentile of the per-shuffle maximum? (Zixi, scientist)
8. Adopt `p_blockswap` alongside `p_n1` (section 4, Step 3 limitation)? (Zixi)
9. Minima: 10 cells, B_task >= 5 N, 300 NREM frames per sleep epoch; zero-variance cells dropped from all epochs? (Zixi, scientist)
10. The team brief's M3 and M4 "Needs" cells are cut off at the screenshot edge: is the full text "at least one significant TASK component" and "at least two significant components"? (brief owner)
11. Who locks the test thresholds in section 5, and by when? (scientist; recommended 15:00)
12. One journal per engineer under `journal/`, or one shared `JOURNAL.md`? (all)
