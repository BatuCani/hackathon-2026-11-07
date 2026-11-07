# Datasets for the reactivation toolbox

Summary of two dataset searches run on 2026-11-07 for the [team brief](../team-brief.md): one over DANDI (Engineer A) and one over other repositories (Engineer B: CRCNS, G-Node GIN, Zenodo, figshare, Dryad, OSF and paper data statements).
Translated and merged from the two German scout reports.
No data files are stored in this repo.

The brief's criterion: deconvolved (or deconvolvable) calcium data, PRE / TASK / POST from the same cells, sleep stages, and a usable licence.

## Result

No dataset qualifies strictly.
DANDI has no two-photon dataset with sleep recordings: all 2P calcium sets found there (for example Allen Institute, Giocomo lab `000054`, `001361`) are awake behaviour or VR only.
Outside DANDI, no hit combines calcium, the same cells across PRE, a real task and POST sleep, sleep stages and an open licence.

**Top pick: the RIKEN cortex dataset**, the fallback the brief names, with a wake bout between two sleep bouts standing in for TASK.
**Alternative: DANDI:000718**, the best calcium candidate on DANDI, if a real task is wanted.

## Ranked table

| Rank | Name | Link / DOI | Modality | Region | Cells / sessions | PRE/TASK/POST | Sleep labels | Licence | Verdict | What is missing |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | RIKEN CBS, *Single-cell calcium imaging dataset of large-scale neuronal activity across wakefulness, sleep, and anesthesia* (Oomoto, Kiyooka, Oizumi, Murayama) | [10.60178/cbs.20260708-001](https://doi.org/10.60178/cbs.20260708-001); Zenodo copy [10.5281/zenodo.17667863](https://doi.org/10.5281/zenodo.17667863) | Wide-field 2P (FASHIO-2PM), G-CaMP7.09, OASIS-deconvolved | Mouse cortex L2/3 (including MOs, MOp, SSp, RSP) | 6574-10197 QC-passed neurons per session; 6 wake-sleep sessions (plus 4 wake + isoflurane) | Same cells within a session; no task, a wake bout between sleep bouts stands in for TASK | Per frame: wake, quiet wake, NREM, REM | CC BY 4.0 (Zenodo API) | partial, top pick | Learning task, stimulus frames; sleep-wake-sleep bout order not checked in the file |
| 2 | Zaki, Pennington, Cai et al., *Offline ensemble co-reactivation links memories across days* (Nature 2025) | [DANDI:000718](https://dandiarchive.org/dandiset/000718/draft) | 1P Miniscope v4.4 (GCaMP), Minian (CNMF-E / OASIS) + wireless EEG/EMG | Mouse dorsal CA1 | About 200-500 cells per mouse; 20 NWB assets, 2 mice | Yes: neutral exposure / fear conditioning / offline homecage rest; cells registered across days in `ses-Week.nwb` | From EEG/EMG; NREM/REM split not checked in the files | CC-BY-4.0 | partial, DANDI alternative | 1P, not 2P; a secondary source says the deposit is incomplete |
| 3 | Han et al. 2025, 24 h mPFC multimodal dataset | [GIN](https://gin.g-node.org/HanJiaying/24hours_mPFC_multimodal_neural_activity_and_natural_behavior_dataset), [10.12751/g-node.1762hn](https://doi.org/10.12751/g-node.1762hn) | Miniature 2P, GCaMP6f, 1.92 Hz (mouse 5: 0.96 Hz), ΔF/F only | Mouse mPFC | More than 50 neurons per FOV; 5 mice, 6 recordings over 24 h | No task (homecage) | W, NR, R, MA, 10 s epochs from EEG/EMG plus video, tied to frames | CC BY 4.0 (licence file read) | partial | Deconvolution, task; mouse 4 part 2 only coarsely labelled |
| 4 | Formozov, Chini, Yang, Wiegert, CA1 sleep / wake / anaesthesia | [GIN](https://gin.g-node.org/SW_lab/Anesthesia_CA1), [10.12751/g-node.lkx6kk](https://doi.org/10.12751/g-node.lkx6kk) | 2P, Suite2p | Mouse CA1 | 3 animals, 54 natural-sleep recordings of 2.1-14.8 min | No | Sleep scoring in a separate folder, not confirmed as frame labels | CC0 1.0 | partial | PRE/TASK/POST; recordings are short |
| 5 | Zhou et al., eLife 2018 | [10.5061/dryad.8ct101p](https://doi.org/10.5061/dryad.8ct101p), Zenodo 4970949 | Endoscope GCaMP6 + LFP | Mouse hippocampus | `Cadata.mat` 192 621 649 bytes | No structured PRE/TASK/POST | Exploration, quiet wake, SWS, REM | CC0 | partial | Deconvolution not documented, PRE/TASK/POST |
| 6 | NDNF interneurons, V1 | [10.5281/zenodo.13921467](https://doi.org/10.5281/zenodo.13921467) | Miniscope nVista/nVoke, dF/F0 | Mouse V1 L1, NDNF interneurons only | 3 MAT files, about 70 MB per mouse | Sleep deprivation protocol, no task | EEG/EMG sleep stages, synchronised | CC BY 4.0 | partial | Population (one interneuron type), task |

### Not calcium (electrophysiology), listed for reference

| Name | Link / DOI | Why listed | Licence | Verdict |
|---|---|---|---|---|
| Grosmark & Buzsáki 2016 | [DANDI:000044](https://dandiarchive.org/dandiset/000044/0.261106.0236); CRCNS hc-11 | Silicon probes, rat CA1, PRE 4 h / maze 45 min / POST 4 h, NREM annotated | CC-BY-4.0 | no, not calcium |
| Girardeau et al. 2017 | [DANDI:000061](https://dandiarchive.org/dandiset/000061/0.250624.0426) | Tetrodes / probes, CA1 and BLA, PRE sleep / shock task / POST sleep | CC-BY-4.0 | no, not calcium |
| Watson et al. 2016 | [DANDI:000041](https://dandiarchive.org/dandiset/000041/0.261104.0300) | Silicon probes, frontal cortex, spontaneous sleep with wake/NREM/REM, no task | CC-BY-4.0 | no, not calcium, no task |
| Eckert, McNaughton, Tatsuno 2020 | [10.5061/dryad.7d7wm37rn](https://doi.org/10.5061/dryad.7d7wm37rn), Zenodo 4992158 | Rat M1 tetrodes, sleep before and after reach training, PCA reactivation after Peyrache; the methods model | CC0 | no, not calcium |
| Lemke et al., eLife 2021 | [10.7272/Q6KK9927](https://doi.org/10.7272/Q6KK9927), Zenodo 5098557 | Rat corticostriatal skill learning and NREM, 108 GB | CC0 | no, not calcium |
| CRCNS hc-25 | [crcns.org](https://crcns.org/data-sets/hc) | PRE sleep, task, POST sleep, tetrodes; CRCNS account needed | CRCNS terms | no, not calcium |
| Dryad 10.5061/dryad.18931zd1w | [10.5061/dryad.18931zd1w](https://doi.org/10.5061/dryad.18931zd1w) | Juvenile rat M1/M2/mPFC, sleep and wake | not recorded | no, not calcium |

Also checked and rejected: CRCNS cai-2, cai-3 and hc-30 (calcium, but anaesthesia/wake or linear track without NREM structure), DANDI:001361 and DANDI:000054 (2P CA1, awake VR only), DANDI:002047 (1P CA1, behaviour tests, no sleep), DANDI:001888 (EEG only), Dryad kh189323d (lateral hypothalamus, feeding and REM), Dryad 6hdr7sqz5 (haemodynamics), Zenodo 15295720 (no files), figshare (no datasets) and OSF (no qualifier in the top hits).

## Top pick: RIKEN cortex dataset

- Portal: https://neurodata.riken.jp/id/20260708-001/ (version 3.0), DOI https://doi.org/10.60178/cbs.20260708-001; version 2.0 is https://doi.org/10.60178/cbs.20260409-001.
- Stable download: https://doi.org/10.5281/zenodo.17667863 (`mouse_data.zip`, used by the lab's loading guide https://github.com/oizumi-lab/mouse_network_2P).
- Data description: bioRxiv https://doi.org/10.64898/2026.07.20.739676.
  The DANDI report also names Kiyooka, Oomoto, Oizumi, Murayama et al. (2026), Cell Reports 45(2): 116902, as the reference paper.

Licence: the Zenodo API gives `cc-by-4.0` for record 17667863, the CBS Data Use Policy on https://neurodata.riken.jp/ says platform research data is CC BY 4.0, and CiNii gives CC BY 4.0 for version 2.0.
The version 3.0 HTML page is an empty single-page app and does not show the licence text.
A secondary blog named CC BY-NC-ND for the Scientific Data rights; that is not on the dataset or policy page that was read.
Use the Zenodo copy with its explicit CC BY 4.0, and cite Oomoto et al. and the CBS DOI.

Cumulative time per sleep session, in seconds, from table 2 of the data description (order: mouse01, mouse02, mouse03, mouse04 day 1, mouse04 day 2, mouse05):

| State | mouse01 | mouse02 | mouse03 | mouse04 d1 | mouse04 d2 | mouse05 |
|---|---|---|---|---|---|---|
| Wake | 320 | 1133 | 471 | 578 | 2052 | 1411 |
| Quiet wake | 98 | 82 | 107 | 4 | 71 | 25 |
| NREM | 732 | 1230 | 1743 | 1627 | 973 | 997 |
| REM | 72 | 0 | 123 | 235 | 42 | 51 |

These are cumulative durations, not a bout list.

### Fetch

The archive is 1 865 754 335 bytes.
It holds `mouse_data/sleep_data.mat` (1 185 449 811 bytes uncompressed), `ane_data.mat` (539 MB) and result files.
The sleep matrix is deflate-compressed, so the whole ZIP is needed; no single-session download URL works (the portal serves the SPA).

```bash
curl -L --fail --output mouse_data.zip \
  "https://zenodo.org/records/17667863/files/mouse_data.zip?download=1"
unzip mouse_data.zip mouse_data/sleep_data.mat
```

### Loader notes

Mapping to the loader fields in the brief:

- `deconv` from `spike_deconv` (OASIS from ΔF/F, N×T), not from `spike_smoothed` (Gaussian, 15 frames, 1.96 s); `dFF` is also present.
- `sleep_stage` from `state`; sleep sessions contain wake, quiet wake, NREM and REM.
  EEG/EMG were classified in 4 s windows, and epochs shorter than 12 s were merged with neighbouring epochs.
- `session_type` = spontaneous; `data_info.recording` is `sleep` or `anesthesia`, so use only the `sleep` sessions.
- `stim_frames`: absent.
- `fs` = 7.65 Hz.
- PRE / TASK / POST must be cut by the loader from the state sequence: NREM before a wake bout, the wake bout, NREM after it.

Not verified: that `sleep_data.mat` uses the variable names from table 1 of the data description (no file was opened), and that each session really has a sleep-wake-sleep order.
Each sleep session contains both wake and NREM per table 2, and figure 1b shows mixed labels under one trace, but the bout assumption in the brief is still an assumption.

## Alternative: DANDI:000718

- https://dandiarchive.org/dandiset/000718/draft (version `0.260825.1902`), 37.85 GB in total, sessions of 2.0-4.5 GB.
- Subjects `sub-Ca-EEG2-1` and `sub-Ca-EEG3-4`.
- PRE: `ses-NeutralExposure_image+ophys.nwb`.
  TASK: `ses-FC_image+ophys.nwb` (fear conditioning with three 2 s foot shocks at 1 min intervals).
  POST: `ses-OfflineDay1Session1_ophys.nwb` / `ses-OfflineDay2Session1_ophys.nwb` (1 h homecage rest/sleep).
  Cross-day cell registration: `ses-Week.nwb`.
- Caveats: 1P miniscope, not 2P; the per-frame sleep staging from EEG/EMG and the deconvolved trace still need checking in the NWB files; a secondary source says the deposit is incomplete.

Fetch only the sessions needed:

```bash
# TASK, sub-Ca-EEG2-1, fear conditioning, 2.05 GB
curl -L -o sub-Ca-EEG2-1_ses-FC_image+ophys.nwb \
  "https://api.dandiarchive.org/api/assets/c2ca0ae4-f5d1-4fed-948f-a727f5e8b5a2/download/"
# POST, sub-Ca-EEG2-1, 1 h homecage sleep/wake, 4.45 GB
curl -L -o sub-Ca-EEG2-1_ses-OfflineDay2Session1_ophys.nwb \
  "https://api.dandiarchive.org/api/assets/30c993ba-cda2-4d04-84a2-c22372afc865/download/"
# cross-session cell alignment
curl -L -o sub-Ca-EEG2-1_ses-Week.nwb \
  "https://api.dandiarchive.org/api/assets/0ce578db-2786-47d7-bf9a-fee3abf2ebd9/download/"
```

Streaming instead of downloading works with `fsspec` + `h5py` / `pynwb` on the S3 blob, for example `https://dandiarchive.s3.amazonaws.com/blobs/244/448/24444885-a283-4b06-ab39-398b998892a2` for the `ses-FC` session of `sub-Ca-EEG2-1`.

## Search method

- DANDI: REST API `https://api.dandiarchive.org/api/dandisets/`, all 953 dandisets scanned, keywords including sleep, NREM, reactivation, replay, two-photon sleep, miniscope sleep, calcium imaging sleep, ophys sleep, EEG two-photon, RIKEN, slow wave, offline, spontaneous, consolidation; metadata and asset lists read for the promising candidates.
- Other repositories: metadata, API listings, HTTP HEAD and one ZIP table of contents via range request; no full downloads.

## Detailed scout and vetting reports

- [calcium-vetting.md](calcium-vetting.md): Deep file-by-file vetting report of candidate calcium datasets against the loader specification.
  Covers verified contents of RIKEN CBS Zenodo 17667863, exact variable names, the one-session finding, recommended splits A and B, loader field mappings, and why DANDI:000718 fails for NREM sleep reactivation.
- [ephys.md](ephys.md): Comprehensive survey of open electrophysiology datasets for full replay and reactivation analysis against Tingley & Peyrache (2020) criteria.
  Identifies Grosmark & Buzsáki 2016 (DANDI:000044 / CRCNS hc-11) as fully qualifying and Gonzalez & Vöröslakos 2026 (DANDI:001695) as the leading near-miss.

