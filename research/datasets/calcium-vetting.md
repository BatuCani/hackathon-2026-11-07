# Dataset vetting: sleep reactivation on calcium imaging data

Scout and vetting report, 2026-11-07.
Scope: independent literature search and file-by-file vetting of top candidate datasets against the loader table of the team brief.
The full RIKEN Zenodo archive was downloaded and `sleep_data.mat` was opened and inspected directly.

## Summary

1. No public dataset strictly satisfies all required criteria (calcium imaging, PRE-sleep / TASK / POST-sleep from the exact same cells, verified sleep stages, and open license).
2. **Recommendation: RIKEN CBS Zenodo 17667863, `mouse_data/sleep_data.mat`** (CC BY 4.0), using a wake bout between NREM phases as a proxy for TASK, as anticipated in the project brief.
   Directly opened and verified: variables, shapes, state encoding, and NREM -> wake -> NREM sequences exist.
3. **Key findings correcting or clarifying prior archive reports:**
   - The Zenodo archive contains **only one sleep session** (6,920 cells x 19,000 frames, 41.4 min), not six.
     Its durations match mouse05 in Table 2 of the data description to the exact second.
     Evaluating method M2 across multiple independent sessions is therefore not directly feasible.
   - The variable names in the file are `spike`, `smoothed_spike`, `dFF`, `state.state`, `state.EMG`, `frame.used_frame`, `frame.boundary_ind`, `ROIs.atlasID`, and `ROIs.Centroid`.
     There is **no** `spike_deconv` and **no** `fs` in the file.
   - The session consists of **two discontinuous segments** of 9,500 frames each (`boundary_ind = [9500, 19000]`).
   - **DANDI:000718 (Zaki et al.) fails:** streamed and checked directly via S3.
     Each deposited offline phase contains only Session1 (10 min), and its sleep intervals contain **zero NREM frames** (only `wake` and `quiet wake`).
     According to cell registration in `ses-Week.nwb`, 19 offline sub-sessions took place on Day 2, but only Session1 is deposited on DANDI.

## Ranking

| Rank | Dataset | Verdict | Missing parts | How the loader derives them |
|---|---|---|---|---|
| 1 | RIKEN CBS / Zenodo 17667863, Kiyooka, Oomoto, ..., Murayama, Oizumi; 2P wide-field cortex L2/3, `sleep_data.mat` | **partial** (best available) | No task, no `stim_frames`. Only 1 session / 1 mouse. `fs` missing from file. No cell IDs. | TASK = selected wake bout, PRE/POST = NREM frames before/after within same segment. `fs = 7.65` from data description. `session_type = spontaneous`. `mouse_id = mouse05`, `session_id = sleep01`, `cell_id = 0..6919`. `stim_frames` empty (M1-M4 do not need them). |
| 2 | Chang, Esteves et al. 2023 Nat Commun (Mohajerani lab), Dryad doi:10.5061/dryad.1ns1rn91c, CC0; 2P M2 L2/3, 14 mice | **partial** | **No sleep stages**: REST1/REST2 are quiet wakefulness without EEG/EMG. Only hippocampal LFP (SWR). | `sleep_stage` cannot be derived, at best "quiescence" as proxy. Good PRE/TASK/POST design with multiple sessions, but no sleep. Single 9.5 GB `data.tar.gz`, no single-session access. |
| 3 | Han et al. 2025, 24 h mPFC miniature 2P, GIN doi:10.12751/g-node.1762hn, CC BY 4.0 | **partial** | No task, dF/F only, 1.92 Hz. | OASIS on `dff`. Wake bout as TASK similar to RIKEN. Label file is a MATLAB opaque object, unreadable by scipy. |
| 4 | Oesch et al. 2020 PNAS, Dryad doi:10.5061/dryad.kh189323d, CC0; miniscope lateral hypothalamus + EEG/EMG | **partial** | Target region outside scope. Effect is REM-specific. Raw traces, not deconvolved. Strict daily PRE/TASK/POST unclear. | OASIS on traces. Sleep stages from supplied EEG/EMG scores. Not opened directly (8.5 GB). |
| 5 | DANDI:000718, Zaki et al. 2025 Nature (Cai lab), CC BY 4.0; 1P miniscope CA1 + EEG/EMG | **no** (as deposited) | **No NREM** in deposited offline sessions. Offline sub-sessions 2-19 missing. For `sub-Ca-EEG3-4`, `ses-Week.nwb` is missing; for `sub-Ca-EEG2-1`, `OfflineDay1Session1` is missing. Only 2 mice. | Cannot be repaired without missing files. Otherwise ideal: `Deconvolved` (Minian), 14.9 Hz, `SleepIntervals`, `ShockStimuli`, cell registration. |
| 6 | Li, Zhao et al. 2025 Sci Rep (Gandhi lab), Dryad doi:10.5061/dryad.nk98sf821, CC0; miniscope CA1 | **partial/no** | No PRE sleep. SWS calcium apparently not included (README lists only LFP for SWS). | Not opened. |
| - | Formozov et al. CA1 (GIN, CC0), Zhou et al. eLife 2018 (Dryad, CC0), NDNF V1 (Zenodo 13921467) | **no / partial** | No PRE/TASK/POST structure. Short recordings or single interneuron subtype. | See sibling dataset reports. |

### Ideal designs with non-public data (data available upon request or upon publication)

From literature search and Data Availability statements in Europe PMC:

- Ghandour et al. 2025 Nat Commun, doi:10.1038/s41467-025-58860-w (Inokuchi lab, Toyama).
  CA1 miniscope + EEG/EMG, NREM1/REM1 -> learning -> NREM2/REM2, same cells.
  Data will be deposited after further publications.
  Code: Zenodo 14963950 / 14978317.
  Best candidate for a future data request.
- Abdou et al. 2024 Nat Commun, doi:10.1038/s41467-024-48816-x (Inokuchi lab).
  ACC microendoscope, EEG/EMG, NREM/REM before and after learning.
  Data available upon request.
- Ghandour et al. 2019 Nat Commun, doi:10.1038/s41467-019-10683-2.
  Data available upon request.
- Choi, Carmichael, Williams, Etter, bioRxiv doi:10.1101/2024.09.05.611474.
  CA1 miniscope + LFP/EMG, sleep before and after task.
  Data available upon publication.
- Lines & Yuste, bioRxiv doi:10.1101/2023.04.26.538480.
  V1 2P + ECoG/EMG, rest -> stimulation -> rest.
  No data statement.
- Srinivasan et al. 2025 Nat Commun (REM only, imaging upon request).
  Grosmark et al. 2021 Nat Neurosci (quiet wake only, upon request).
  Adv Sci 2024 doi:10.1002/advs.202400662 (NREM cueing, upon request).
- Adv Sci 2026 doi:10.1002/advs.202509707 (A1 2P in SWS): Zenodo 15530880 marked CC-BY, but API returns restricted access with no downloadable files.
- Excluded: Chang et al. 2025 Nature ("Sleep microstructure organizes memory replay") is electrophysiology, not calcium imaging.
  PhysioNet Landsness is wide-field cortical imaging without single-cell resolution.

## Detail 1: RIKEN `sleep_data.mat` (opened and verified)

### File retrieval and integrity

- Zenodo record 17667863: `mouse_data.zip` (1,865,754,335 bytes, MD5 `d611c4577b4e3a32762860fa4ab7b5f6`, matching Zenodo API).
- Target file: `mouse_data/sleep_data.mat` (1,185,449,811 bytes, MATLAB 5.0 format, created Fri Aug 22 20:05:33 2025).
- Record title: "Dataset for 'Single-cell resolution functional networks during unconsciousness are segregated into spatially intermixed modules'", published 2025-11-21, CC BY 4.0 license.
- Authors: Kiyooka, Oomoto, Kitazono, Saito, Kobayashi M., Matsubara, Kobayashi K., Murayama, Oizumi.
- Required file: only `mouse_data/sleep_data.mat`.
  `ane_data.mat` (wake + isoflurane) and `results/` are not needed.

### Variables (header inspected, then selectively loaded)

| Variable | MATLAB class | Shape | Size in file | Content |
|---|---|---|---|---|
| `ROIs` | struct | 1x1 | 0.1 MB | `atlasID` (6920, uint16, 13 areas), `Centroid` (6920x2) |
| `dFF` | double | 6920 x 19000 | 1010 MB | dF/F fluorescence traces |
| `frame` | struct | 1x1 | <0.1 MB | `used_frame` (Cell 1x2), `boundary_ind = [9500 19000]` |
| `smoothed_spike` | double | 6920 x 19000 | 151 MB | Smoothed spikes; do **not** use |
| `spike` | double | 6920 x 19000 | 24 MB compressed | **Deconvolved spikes (OASIS) -> target for `deconv`** |
| `state` | struct | 1x1 | 0.1 MB | `state` (19000, double), `EMG` (19000, double) |
| `st` | MATLAB opaque (class 17, likely atlas table) | - | - | scipy cannot read it; not needed |
| `data_info` | char | 1x5 | - | `'sleep'` |

Following these is an unnamed element (class 9, 1x214208), likely the MCOS subsystem block for `st`.
The variable list aligns with documentation in the official loader `load_data_demo.m` (github.com/oizumi-lab/mouse_network_2P): "dFF: NxT", "spike: NxT deconvolved spike matrix", "SleepState: 0: Awake, 0.5: Quiet wake, 1: NREM, 2: REM", "boundary_ind: ... frames are not recorded continuously".

Important technical note: calling `scipy.io.whosmat` or `scipy.io.loadmat` without `variable_names` fails on the opaque object `st` (`TypeError: 'NoneType' object is not iterable`).
The loader must specify:
`scipy.io.loadmat(path, variable_names=['spike', 'state', 'frame', 'ROIs'], squeeze_me=True, struct_as_record=False)`

### Properties of the `spike` matrix

- 6920 x 19000 float64, no NaNs, min 0, max 2.85.
- 98.7% zeros; on average a cell is active in 1.3% of frames.
- Matches raw OASIS deconvolution output and satisfies the requirement for raw, unsmoothed spike events.

### State encoding (`state.state`)

| Value | Meaning (per loader documentation) | Frames | Seconds at 7.65 Hz |
|---|---|---|---|
| 0 | Wake | 10,791 | 1,411 |
| 0.5 | Quiet wake | 189 | 25 |
| 1 | NREM | 7,625 | 997 |
| 2 | REM | 390 | 51 |
| 0.0287-0.032 | Non-canonical transition values | 5 (frames 7305, 11618, 12997, 13717, 16145) | - |

The five non-canonical values sit precisely at bout boundaries as interpolation artifacts.
The loader should round them to 0 or mark them as unscored.
The state durations match mouse05 in Table 2 of the data description to the exact second (Wake 1,411 s, NREM 997 s, REM 51 s, Quiet wake 25 s).
**The Zenodo archive contains only mouse05, not six independent sleep sessions.**
`used_frame{1}` (9,146 frames) contains only state 0; `used_frame{2}` (5,660 frames) contains only state 1 (authors' stationary selections, optional for our pipeline).
`fs` is absent from the file: 9,500 frames per segment correspond to 20.7 min at 7.65 Hz.
This rate must be supplied as a constant in the loader.

### Bout sequences (Wake = 0 and 0.5 grouped as W*)

Segment 0, frames 0-9500 (20.7 min):
`W* 41s, NREM 20s, W* 313s, NREM 27s, W* 35s, NREM 43s, W* 94s, NREM 35s, W* 63s, NREM 44s, W* 239s, NREM 17s, W* 87s, NREM 65s, W* 69s, NREM 48s`

Segment 1, frames 9500-19000 (20.7 min):
`W* 53s, NREM 36s, W* 27s, NREM 74s, W* 87s, NREM 20s, W* 38s, NREM 42s, W* 81s, NREM 71s, W* 24s, NREM 36s, W* 12s, NREM 69s, REM 51s, W* 85s, NREM 19s, W* 45s, NREM 16s, W* 13s, NREM 224s, W* 17s, NREM 30s, W* 13s, NREM 60s, W* 1s`

Total NREM per segment: 2,299 frames (300 s) in Segment 0; 5,326 frames (696 s) in Segment 1.
Sleep is fragmented into many 20-70 s bouts.
**An NREM -> wake -> NREM sequence exists multiple times in both segments.**

Wake bouts >= 60 s with preceding and following NREM (frames 0-indexed):

| Segment | Frames | Duration | NREM before / after in same segment | NREM before / after in entire session |
|---|---|---|---|---|
| 0 | 468-2866 | **313 s (longest)** | 155 fr (20 s) / 2144 fr (280 s) | 155 / 7470 |
| 0 | 3674-4393 | 94 s | 696 (91 s) / 1603 (210 s) | 696 / 6929 |
| 0 | 4662-5146 | 63 s | 965 (126 s) / 1334 (174 s) | 965 / 6660 |
| 0 | 5481-7306 | **239 s** | **1300 (170 s) / 999 (131 s)** | 1300 / 6325 |
| 0 | 7439-8105 | 87 s | 1433 (187 s) / 866 (113 s) | 1433 / 6192 |
| 0 | 8601-9130 | 69 s | 1929 (252 s) / 370 (48 s) | 1929 / 5696 |
| 1 | 10954-11619 | 87 s | 842 (110 s) / 4484 (586 s) | 3141 / 4484 |
| 1 | 12381-12998 | 81 s | 1313 (172 s) / 4013 (525 s) | 3612 / 4013 |
| 1 | 15006-15657 | 85 s | **2657 (347 s) / 2669 (349 s)** | 4956 / 2669 |

Regarding the longest wake bout: frames 468-2866 (313 s) is preceded by only 155 NREM frames (20 s) and followed by 2,144 frames (280 s) within the segment.
That is insufficient sleep for a balanced PRE epoch.

### Recommended splits

Splits must be contained within a single recording segment because the boundary index marks a discontinuous recording gap.

- **Split A (Segment 0)**: TASK = frames 5481-7306 (239 s wake), PRE = 1,300 NREM frames (170 s), POST = 999 NREM frames (131 s).
  Provides the most balanced compromise between a long wake TASK epoch and sufficient, balanced PRE/POST sleep.
- **Split B (Segment 1)**: TASK = frames 15006-15657 (85 s wake), PRE = 2,657 NREM frames (347 s), POST = 2,669 NREM frames (349 s).
  Offers the largest volume of NREM frames, although with a shorter TASK epoch (650 frames).
- Splits A and B provide two independent segments from the exact same cells, giving method M2 two pseudo-sessions.
  They are not true independent experimental sessions because they share the same animal and lack an intervening behavioral learning task.

### Loader mapping for RIKEN

| Field | Source | Status |
|---|---|---|
| `sleep_stage` | `state.state`: 0 and 0.5 -> wake, 1 -> NREM, 2 -> REM, other -> unscored | Present |
| `deconv` | `spike` (6920 x 19000) | Present, raw OASIS |
| `session_type` | Constant `spontaneous` | Derived |
| `stim_frames` | No task -> empty; TASK window serves as pseudo-epoch | Absent (by design) |
| `fs` | 7.65 Hz from data description (bioRxiv doi:10.64898/2026.07.20.739676) | Supplied as constant |
| `cell_id` | Row index 0..6919; cortical area from `ROIs.atlasID` | Derived |
| `mouse_id`, `session_id` | `mouse05` (from Table 2 cross-reference), `sleep` | Derived |
| Identical cells PRE/TASK/POST | Yes, single continuous imaging field | Verified |
| Sessions | 1 (two recording segments) | Limitation for M2 |
| NREM frames per epoch | See split table (999-2669) | Sufficient for M1/M3/M4 |
| License | CC BY 4.0 (Zenodo API) | Verified |

Memory management: load only `spike` (1.0 GB as float64, 0.5 GB as float32), never load `dFF`.

## Detail 2: DANDI:000718, Zaki et al. (streamed, no full download)

Inspection method: streaming via `h5py` and `remfile` over S3 blob URLs, inspecting metadata and targeted array slices.
Version `0.260825.1902` (draft), 20 assets, 40.6 GB.

`sub-Ca-EEG3-4_ses-OfflineDay1Session1_ophys.nwb`:
- `processing/ophys/Fluorescence/Deconvolved/data`: 8933 frames x 711 cells, timestamps 0.335-600.09 s, dt 0.067 s -> **14.93 Hz, 10 min**.
- Raw video `OnePhotonSeries`: 17876 x 608 x 608 uint8.
- `processing/sleep/SleepIntervals` (14 rows): exclusively `quiet wake` and `wake`, for example "quiet wake 210.9-582.8 s".
  **Zero NREM, zero REM.**
- EEG/EMG/temperature/activity at 500 Hz in `acquisition`.
- `session_description`: "...Mouse behavior and calcium were recorded for an hour."
  However, only 600 s are deposited.

`sub-Ca-EEG3-4_ses-OfflineDay2Session1_ophys.nwb`: 8933 x 783 at 14.93 Hz; 36 intervals, again containing only `wake` and `quiet wake`.
`ses-FC` (EEG3-4): `Deconvolved` 4076 x 783 (274 s), `stimulus/presentation/ShockStimuli`, `processing/behavior/FreezingIntervals`.
`ses-NeutralExposure` (EEG3-4): 8931 x 851 (600 s), no sleep intervals.
`sub-Ca-EEG2-1_ses-Week.nwb`: `intervals/epochs` lists 27 sessions, including `OfflineDay2Session1` through `OfflineDay2Session19` and `OfflineDay1Session1` through `Session5`.
`processing/cell_registration/OfflineDay2SessionNvsConditioningSessions` contains cross-session cell matches (for example 1326 rows, 597 valid matches for FC, 623 for NE, -9999 = not found).

The registration file proves that the 1-hour offline rest was divided into nineteen 10-minute files, and only Session1 is included in the DANDI deposit.
The actual NREM sleep occurred in later sub-sessions that are absent from DANDI.
Verdict: **no** for NREM reactivation as currently deposited.
Filing an inquiry with the Cai lab or DANDI would be worthwhile: the underlying design (NE -> offline -> FC -> offline, shock stimuli, cell tracking, synchronized EEG/EMG) is otherwise strong.

## Detail 3: Han et al., label file

The file `Processed data/#1/part1/Behavior recording_Label.mat` (935 kB, MATLAB 5.0 format) was inspected.
`scipy.io.loadmat` parses `calib` only as `MatlabOpaque` (an MCOS object, likely a table or string container).
The `sleep_stage` field cannot be read in Python without a MATLAB or Octave conversion step.
Because of this dependency, Han et al. remains at Rank 3.

## Reconciliation with prior archive reports

- `hackathon-data-dandi`: previously marked DANDI:000718 "partial" and RIKEN "qualifies".
  Correction: DANDI:000718 has no NREM frames in the deposited offline sessions (verdict: no).
  RIKEN is partial (no behavioral task, only one session in the Zenodo archive).
  The DOI mapping of RIKEN v3.0/v2.0 remains unconfirmed; the actionable source is Zenodo 17667863.
- `hackathon-data-other`: RIKEN was correctly identified as top choice.
  Corrections: variables are named `spike` and `state.state` (not `spike_deconv` and `state`).
  The archive holds only mouse05, not six sessions.
  The presence of NREM -> wake -> NREM sequences is verified: they exist in both segments, though sleep is fragmented.

## Recommendations

1. Dataset: **RIKEN Zenodo 17667863, `mouse_data/sleep_data.mat`**.
2. Loader implementation: `loadmat(..., variable_names=['spike', 'state', 'frame', 'ROIs'])`, `fs = 7.65`, segment boundaries from `boundary_ind`, Splits A and B as defined above, NREM identified by `state == 1`.
3. Analysis methods: execute M1, M3, M4 on Split A and Split B.
   For M2, treat A and B as two pseudo-sessions, explicitly documenting that they derive from the same animal.
4. Citation: Kiyooka D., Oomoto I., ..., Murayama M., Oizumi M. (2025), Zenodo, doi:10.5281/zenodo.17667863, CC BY 4.0; companion data description (bioRxiv doi:10.64898/2026.07.20.739676) and CBS DOI 10.60178/cbs.20260708-001.
5. Optional follow-up: retrieve the remaining five sleep sessions via the RIKEN CBS portal (https://neurodata.riken.jp/id/20260708-001/) to support true multi-session M2 analysis (portal requires browser-based interaction).
6. Optional data request: inquire with the Inokuchi lab (Ghandour 2025, Abdou 2024) for genuine PRE-sleep / learning / POST-sleep calcium datasets.

## Identified risks

- **No true behavioral task**: reactivation of a spontaneous wake bout serves as a proxy.
  Positive results may reflect slow baseline drift or state transition effects rather than memory reactivation.
  Circular shifts (N1) do not control for drift.
  Controls: compare a split with inverted PRE/POST order and evaluate across multiple splits.
- **Single animal and single session**: M2 multi-session analysis relies on pseudo-sessions.
- **Fragmented sleep**: NREM bouts last 20-70 s; boundary frames represent transition states (4 s scoring window, merges under 12 s).
- **Discontinuous segment boundary**: frames 9499 and 9500 are not contiguous.
  Splits must not cross this boundary, and circular shifts for N1 must be performed per segment.
- **`fs` as an external constant**: 7.65 Hz originates from the data description paper, not the MAT file.
- **Opaque object `st`**: naive `loadmat` without explicit `variable_names` fails.
- **RAM footprint**: `spike` as float64 requires 1 GB; full 6,920-cell covariance and PCA matrices require memory management (6920^2 x 8 bytes = 383 MB per matrix).
  Subsetting by cortical area or activity threshold is recommended if needed.
- **Licensing**: Zenodo record explicitly specifies CC BY 4.0.
