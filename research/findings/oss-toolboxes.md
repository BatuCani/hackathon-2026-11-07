# OSS survey: replay and reactivation toolboxes

As of 2026-11-07.
Scout pass, no repo edits; the hackathon repo was not changed.
Translated from the German original; package names, licences, commit pins, file:line evidence and install measurements are kept exactly.
The original table uses an em dash for "not present"; it is written here as "-".

Target pipeline per `research/BUILD_APPROACH.md`: movement-only encoding, candidate bursts, Poisson Bayes, weighted correlation / line fit / rank order, shuffles, synthetically injected replay.
The submission must be Apache-2.0 compatible.
GPL/AGPL is reference only.

Checked via `gh-axi api` (licence file read, not only the SPDX field), PyPI JSON and `uv run --no-project --python 3.12` on macOS arm64 (`cpython-3.12.15`).

Note: this survey was written against the replay pipeline in `BUILD_APPROACH.md`.
For the reactivation toolbox in [../team-brief.md](../team-brief.md), see [tool-fit.md](tool-fit.md).

## Recommendation

**Dependency, commit pin, not the PyPI release:**

- `neurospatial @ git+https://github.com/edeno/neurospatial@0cc33ecd374fd56270b0618aaf82eae5a030da61` (MIT, Eric Denovellis).
  This is the Python toolbox that already has the planned score battery.
- `ripple-detection` 1.7.1 (MIT, Eden-Kramer-Lab), only if LFP or multiunit bursts are needed.

**Pull in, do not write ourselves:** Poisson `decode_position`, weighted correlation, Radon/line fit, rank order, shuffle nulls, PCA/ICA assemblies, EV/REV, `simulate_replay_event`.

**Cite:** Takigawa et al. 2024 and the CC0 repo `bendor-lab/replay_detection_cross_validation` for the two-track log-odds.
Tingley & Peyrache 2020 as the methods framework.
`DavidTingley/RnR_methods` only as the gap that was MATLAB-GPL; do not port.

**Write ourselves:** the speed cut and the one demo command line (config, seed, JSON report).
The sequence-free two-track log-odds check from Takigawa.
Candidate windows only if `ripple-detection.multiunit_HSE_detector` is not enough.

**Do not build in:** anything GPL (RnR_methods, spykshrk, pynacollada, old `replay_classification`, diba-lab/NeuroPy, CADopti).
`nelpy` from PyPI does not import under 3.12.
`neuro_py` depends on a nelpy git pin and states that EV was taken from the GPL package NeuroPy.

Fallback if an unreleased alpha pin is not wanted: decoder and time shuffles from `pynapple` (MIT, PyPI, installs cleanly), scores written briefly ourselves following the CC0 MATLAB files and `nelpy/analysis/replay.py` on GitHub (MIT, as of 2026-10-14).
That is the more expensive day.

## What `neurospatial` on main actually has

Licence file `LICENSE`: MIT, Copyright 2025 Eric Denovellis.
`pyproject.toml` line 7 `license = "MIT"`, line 6 `requires-python = ">=3.10"`, line 37 classifier `Development Status :: 3 - Alpha`.
Default-branch commit `0cc33ecd37` on 2026-11-06 (`test: compare near-zero resultant lengths…`).
GitHub `pushed_at` 2026-11-06.

PyPI `neurospatial` 0.6.0 (uploaded 2026-07-03, tag `v0.6.0`) does not have `src/neurospatial/replay` and `reactivation`: `GET /repos/edeno/neurospatial/contents/src/neurospatial/replay?ref=v0.6.0` answers 404.
`pip install neurospatial` is not enough.

`src/neurospatial/replay/__init__.py` line 1 describes scoring decoded candidates against shuffles.
Line 7 says sharp-wave ripples and population bursts do not belong to this subpackage.
Lines 12, 15 and 18 name `detect_trajectory_radon` (Davidson 2009), `weighted_correlation` (Wu & Foster 2014) and `fit_linear_trajectory` (Karlsson & Frank 2009; Wu 2017).
Lines 54-59: `rank_order_correlation` (Foster & Wilson 2006) and `rank_order_significance`.

Evidence in the modules: `correlation.py:63` `weighted_correlation`; `trajectory.py:1606` `detect_trajectory_radon`, `:717` `fit_linear_trajectory`, `:1061` `regression_line_score`; `rank_order.py:176` `rank_order_correlation`; `nulls.py:44` `shuffle_cell_identity`, plus place-field, posterior and spike-count shuffles; `methods.py:1683` `detect_replay`, `:3238` `detect_rank_order_replay`.

Decoder: `decoding/likelihood.py:8` and `:41` `log_poisson_likelihood` (Poisson, primary model).
`decode_position` imports.

Reactivation: `reactivation/__init__.py:8-16` `detect_assemblies` (ICA/PCA/NMF) and `assembly_reactivation` (Peyrache 2010, van de Ven 2016); `:41-50` `explained_variance_reactivation` (Kudrimoti 1999, REV after Pennartz 2004) and `ev_rev_contrast`.

Synthesis: `simulation/replay.py:1-8` and `:120` `simulate_replay_event` (path plus Poisson spikes from rate maps, with drop and noise).
That is the injected replay control from the build plan.

NWB: optional extra `nwb` (`pyproject.toml:82-86`, `pynwb>=2.5.0`), loader under `src/neurospatial/io/nwb/`.
The core import does not pull in pynwb.

Core dependencies (`pyproject.toml:12-26`): joblib, matplotlib, networkx, numpy, pandas, pot, scikit-image, scikit-learn, scipy, shapely, track-linearization, tqdm, typing_extensions.
JAX only as an extra.

Install, measured:

```text
uv run --no-project --python 3.12.15 \
  --with "neurospatial @ git+https://github.com/edeno/neurospatial@0cc33ecd374fd56270b0618aaf82eae5a030da61" \
  python -c "import neurospatial.replay, neurospatial.decoding, neurospatial.reactivation"
```

Result: build ok, 36 packages, `real 23.65`, arm64, Python 3.12.15.
Then imported: `weighted_correlation`, `rank_order_correlation`, `detect_trajectory_radon`, `decode_position`, `explained_variance_reactivation`, `detect_assemblies`, `simulate_replay_event`.

GitHub code search `repo:edeno/neurospatial log_odds`: 0 hits.
So the two-track log-odds from Takigawa are not covered.

## Table

Column legend: Dec Poisson decoder, RO rank order, WC weighted correlation, LF Radon or line fit, SH shuffles, AS PCA/ICA assemblies, EV EV/REV, RP ripple or burst, NWB NWB reading.
"-" means not present or not seen as an API.

| Package | Dec | RO | WC | LF | SH | AS | EV | RP | NWB | Licence (file) | Last commit on default | Activity | Install Py 3.12 arm64 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neurospatial main `0cc33ecd` | yes | yes | yes | yes | yes | yes | yes | no | extra | MIT | 2026-11-06 | push 2026-11-06, alpha, 1 star | yes, 36 packages, 24 s | **dependency, git pin** |
| neurospatial PyPI 0.6.0 | partial | no | no | no | no | no | no | no | extra | MIT | tag 2026-07-03 | release without `replay/` | not tried separately | skip for this pipeline |
| ripple-detection 1.7.1 | - | - | - | - | - | - | - | yes | - | MIT | 2026-10-29 | push 2026-11-01 | yes, `Kay_ripple_detector` | **optional dependency** |
| pynapple 0.11.4 | yes | - | - | - | yes | - | - | filter | yes | MIT | 2026-10-14 | push 2026-11-06, 383 stars | yes | fallback only, otherwise redundant |
| pynwb 4.2.0 | - | - | - | - | - | - | - | - | yes | BSD-like, see below | 2026-09-16 | push 2026-11-04 | yes | via neurospatial `[nwb]` |
| elephant 1.2.1 | - | - | - | - | yes | CAD, not PCA/ICA | - | - | via neo | BSD-3-Clause | 2026-11-03 | active | yes | skip, duplication |
| nelpy PyPI 0.2.1 | yes, in git | - | - | yes, in git | yes, in git | - | - | claimed | - | MIT | git 2026-10-14 | PyPI stuck at 2019-02-07 | **import fails** | reference only |
| neuro_py (`neuro-analysis-py`) | - | - | yes | yes | yes | yes | yes | - | - | MIT file, EV from GPL | 2026-11-01 | push 2026-11-02 | not installed; git dep nelpy | skip, licence taint |
| replay_trajectory_classification | state space | - | - | - | - | - | - | - | - | MIT | 2025-09-26 | PyPI 1.4.1 from 2024-09-06 | not tried; dask, numba, cupy optional | reference, stretch |
| non_local_detector | HMM/JAX | - | - | - | - | - | - | - | - | MIT | 2026-11-07 | PyPI 0.6.9 from 2024-11-21 | not tried; jax | later, not today |
| dandi 0.82.0 | - | - | - | - | - | - | - | - | client | Apache-2.0 | 2026-11-03 | active | not tried; >40 deps | only if DANDI is streamed |
| neurodsp 2.3.0 | - | - | - | - | - | - | - | burst, generic | - | Apache-2.0 | 2026-09-16 | push 2026-09-16 | yes, light | skip, ripple-detection is closer |
| ghostipy 0.2.2 | - | - | - | - | - | - | - | spectrum | - | Apache-2.0 | 2022-08-15 | cold | not tried; pyfftw, datashader | skip |
| spyglass | wrapped | - | - | - | - | - | - | yes | yes | MIT text, API says NOASSERTION | 2026-10-27 | push 2026-11-07, 121 stars | not tried; DataJoint lab stack | skip |
| bendor `replay_detection_cross_validation` | yes | Spearman | yes | yes | yes | - | - | threshold | - | CC0-1.0 | 2024-09-04 | cold, MATLAB | n/a | reference for log-odds |
| RnR_methods | yes | yes | - | - | yes | PCA/ICA | - | - | - | GPL-3.0 | 2021-05-08 | dead | n/a, MATLAB | reference only |
| spykshrk_realtime (LorenFrankLab) | real time | - | - | - | - | - | - | - | - | GPL-3.0 | 2019-09-03 | `pushed_at` 2024-04-25 | n/a | skip |
| pynacollada | - | - | - | - | - | - | - | tutorials | - | GPL-3.0 | 2025-12-04 | occasional | not tried | reference only |
| replay_classification (Deng 2016) | state space | - | - | - | - | - | - | - | - | GPL-3.0 | 2018-11-28 | dead | n/a | skip |
| diba-lab/NeuroPy | - | - | - | - | - | - | yes | - | - | GPL-3.0 | 2026-10-21 | active | not tried | reference only |
| tortlab/Cell-Assembly-Detection | - | - | - | - | - | PCA/ICA, MATLAB | - | - | - | no licence file | 2020-03-26 | dead | n/a | skip |
| DurstewitzLab/Cell-Assembly-Detection | - | - | - | - | - | CAD, MATLAB | - | - | - | none | 2020-03-31 | dead | n/a | skip |
| DurstewitzLab/CADopti | - | - | - | - | - | CAD, MATLAB | - | - | - | GPL-3.0 | 2020-04-11 | dead | n/a | skip |
| FeeLab/seqNMF, darikoneil/gseqNMF | - | - | - | - | - | seqNMF, not a replay score | - | - | - | MIT | 2024-03-17 and 2026-03-01 | seqNMF niche | not tried | skip for this pipeline |

## Install evidence (Python 3.12.15, arm64)

All with `uv 0.13.0`, `--no-project`, interpreter `/Users/batu/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`.

| Package | Result |
|---|---|
| neurodsp 2.3.0 | import ok, 13 packages, 1.8 s |
| ripple-detection 1.7.1 | import ok, `Kay_ripple_detector` True, 15 s (pandas wheel) |
| pynwb 4.2.0 | import ok, 8 s |
| pynapple 0.11.4 | import ok, `decode_bayes` and `jitter_timestamps` True, 10 s |
| elephant 1.2.1 | import ok, `jitter_spikes` and `cell_assembly_detection` True, 10 s |
| nelpy 0.2.1 | wheel builds, import `ModuleNotFoundError: dill` in `nelpy/auxiliary/_results.py:7` |
| neurospatial git pin | see above |

Not installed, PyPI `requires_dist` only: `replay-trajectory-classification` 1.4.1 (numpy, numba, dask, distributed, scikit-image, regularized-glm, …), `non-local-detector` 0.6.9 (jax, jaxlib, track-linearization, …), `dandi` 0.82.0 (more than 40 runtime deps), `ghostipy` 0.2.2 (pyfftw, datashader, hvplot).
The non_local_detector `README` says PyPI 0.6.9 lags behind `main` and to install from GitHub.

## Individual findings behind the verdict

**pynapple.**
`pynapple/process/decoding.py:157` `decode_bayes`, `:185` Poisson assumption.
`randomize.py:2` surrogates: `shift_timestamps` `:12`, `shuffle_ts_intervals` `:145`, `jitter_timestamps` `:175`.
`io/__init__.py` exports `NWBFile`.
No `weighted_correlation` (code search in the repo: 0).
Licence file MIT.

**pynwb.**
`license.txt` is the three-clause BSD of the University of California / LBNL, plus one sentence on the licence of voluntarily contributed enhancements.
The GitHub API says `NOASSERTION` because the file name `license.txt` is not a standard SPDX match.
Permissive, compatible with Apache-2.0 as a dependency, keep the notices.
No copyleft.

**elephant.**
`cell_assembly_detection.py:1-13` is CAD after Russo 2017 (pairs, lags, agglomeration), not Lopes-dos-Santos PCA/ICA.
`spike_train_surrogates.py` has dither, ISI shuffle, jitter, bin shuffle, trial shift.
BSD-3-Clause in `LICENSE.txt`.
For the hackathon, neurospatial covers assemblies and shuffles.

**nelpy.**
On GitHub, `nelpy/analysis/replay.py:27` Davidson line, `:794` `linregress_ting` (R² of the MAP path), `:1212` `trajectory_score_array` (band mass; parameter `weights` "not yet implemented"), plus time-swap, unit-ID and Poisson shuffles.
No hit on `weighted_correlation`.
PyPI 0.2.1 is the 2019 version and does not import under 3.12.
Unusable as a dependency, usable as a reading template for the older scores.

**Takigawa code.**
`bendor-lab/replay_detection_cross_validation`, `LICENSE` is CC0-1.0.
`Pipeline/Replay scoring and shuffling/` contains `weighted_correlation.m` (1770 B), `line_fitting.m`, `spearman_median.m`, `parallel_shuffles.m`.
`example_code/calculate_log_odds.m` and `generate_linear_replay_events.m` are the sequence-free log-odds example.
MATLAB, so not a pip dependency.
CC0 allows a clean re-implementation of the log-odds in Python.
Do not take over the whole analysis scripts.

**RnR_methods.**
`LICENSE` is GPL-3.0.
`README.md:16-21`: `ReactStrength` (PCA or ICA), `replay_Bayesian`, `replay_RankOrder`.
Last commit 2021-05-08.
Do not copy, do not port.

**spykshrk / ghost.**
`LorenFrankLab/spykshrk_realtime`: GPL-3.0 in the LICENSE file, default-branch commit 2019-09-03.
A repo named ghost for replay decoding does not show up in search.
`kemerelab/ghostipy` is an Apache-2.0 spectral library (MTM), last commit 2022-08-15, not a decoder.

**replay_trajectory_classification.**
MIT, Copyright 2019 Eric Denovellis.
README lines 16-33: state space, sorted or clusterless spikes, trajectory type, GPU via cupy.
Paper Denovellis 2021 eLife.
This is not the naive-Bayes-plus-score pipeline.
PyPI lags behind the repo (commit 2025-09-26).

**non_local_detector.**
MIT, Copyright 2023 Eric Denovellis.
README: HMM for non-local activity, JAX.
Commit on `main` 2026-11-07.
Too heavy for the one-day slice.
The same person now maintains `neurospatial`, where the score layer lives.

**neuro_py.**
Repo LICENSE MIT, Copyright 2023 Ryan Harvey.
`neuro_py/ensemble/replay.py` has `weighted_correlation` (`:507`) and `WeightedCorr`.
`explained_variance.py:23` says "Adapted from https://github.com/diba-lab/NeuroPy".
That upstream repo is GPL-3.0 (API, as of 2026-10-21).
`pyproject.toml` pins `nelpy @ git+https://github.com/nelpy/nelpy.git`.
The PyPI name `neuro-analysis-py` 0.0.2 is a 2023 upload, not this tree.
Do not depend on it.

**Assemblies without a licence.**
`tortlab/Cell-Assembly-Detection` (Lopes-dos-Santos, MATLAB): GitHub API `license: NONE`, no LICENSE in the root, commit 2020-03-26.
Do not use.
The licensed PCA/ICA route is `neurospatial.reactivation.detect_assemblies`.

## What we write ourselves

1. Run versus rest via an explicit speed threshold, and freezing the rate maps.
   neurospatial encodes; the epoch rule is the experiment, not the library.
2. Candidate intervals.
   For LFP: `Kay_ripple_detector` and relatives in `ripple_detection/__init__.py`.
   For spikes without LFP: `multiunit_HSE_detector` in `src/ripple_detection/detectors/_hse.py:58`.
   Thresholds and minimum duration stay config.
3. Two-track log-odds after Takigawa, following `example_code/calculate_log_odds.m` (CC0), because neurospatial does not export it.
4. One command that writes `simulate_replay_event` as the positive control, a shuffle as the negative control, and the posterior plus score plus p to JSON.
   Seeds and parameters next to the result, as `BUILD_APPROACH.md` requires.

Do not rewrite: Poisson posterior, weighted correlation, Radon, linear fit mass, rank order, cell-ID shuffle, PCA/ICA, EV/REV.

## Apache-2.0

MIT (`neurospatial`, `ripple-detection`, `pynapple`) and BSD-3 (`elephant`, `pynwb`) may sit next to Apache-2.0 code if the notices are kept.
GPL-3 (`RnR_methods`, `spykshrk_realtime`, `pynacollada`, `replay_classification`, `NeuroPy`, `CADopti`) must not go into the submitted tree and not be an imported dependency.
Avoid `neuro_py` despite its MIT file, as long as its EV module names a GPL template.
