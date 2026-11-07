# Calcium-imaging sleep/reactivation datasets: verified lookup (2026-11-07)

Rule used: an item is listed only if a live lookup in this session returned it (DANDI API, Zenodo API, Europe PMC REST, firecrawl scrape of the repository page). Anything I could not confirm is marked UNVERIFIED. No data downloaded (only metadata pages and API JSON).

## Bottom line

Nothing fully qualifies. No public record found that has all of: deconvolved calcium + PRE sleep / TASK / POST sleep from the SAME cells + EEG/EMG-based NREM/REM labels + an open licence + a loader-ready format.

- PICK (best partial match for the PRE/TASK/POST test itself): **G-Node GIN "PFC Calcium Imaging Dataset"**, doi:10.12751/g-node.b8k1yn, CC BY 4.0, 1.4 GiB zip. 1p mPFC calcium, 4 mice, home-cage sleep recorded before AND after learning, task days, cells tracked across all sessions (CellReg). Weakness: no EEG/EMG/LFP, so no NREM/REM labels (only "sleep epochs", method of defining them UNVERIFIED). Sleep is not staged, so treat it as "sleep vs task" only.
- FALLBACK (the named one): **RIKEN CBS "Single-cell calcium imaging dataset ... wakefulness, sleep, and anesthesia"**, doi:10.60178/cbs.20260708-001 (v3), CC BY 4.0. Only dataset with deconvolved spikes + EEG/EMG-derived wake/quiet-wake/NREM/REM labels, but there is no task: a wake bout between two sleep bouts has to stand in for TASK, and whether any session contains sleep-wake-sleep order is UNVERIFIED (Table 2 durations not seen).
- Honourable mention (cannot be loaded as calcium): DANDI:000718 has the right biology (offline sleep/wake after encoding, EEG/EMG staging in the paper) but only 2 subjects in DANDI, 40.6 GB, and I could not verify that sleep labels or deconvolved traces are inside the NWB files.

## 1. RIKEN fallback dataset (task 1): verified facts

| Field | Value | Source (live) |
|---|---|---|
| Title (data descriptor) | Multi-area single-cell calcium imaging dataset of the mouse cortex across wakefulness, sleep, and anesthesia | nature.com/articles/s41597-026-08202-2 (Sci Data, published 2026-09-10, DOI 10.1038/s41597-026-08202-2; bioRxiv 10.64898/2026.07.20.739676) |
| Title (repository record) | Single-cell calcium imaging dataset of large-scale neuronal activity across wakefulness, sleep, and anesthesia | neurodata.riken.jp/id/20260708-001 |
| Authors | Ikumi Oomoto, Daiki Kiyooka, Masafumi Oizumi, Masanori Murayama (RIKEN CBS; Univ. Tokyo) | same |
| Repository | RIKEN CBS Data Sharing Platform (neurodata.riken.jp). Not DANDI, not Zenodo. Mirror: SSBD repository ssbd-repos-000538 (DOI 10.24631/ssbd.repos.2026.08.538) | SSBD page |
| IDs / DOIs | v3: accession 20260708-001, doi:10.60178/cbs.20260708-001 (adds raw TIFF + EEG/EMG). v2: 20260409-001, doi:10.60178/cbs.20260409-001 (processed only). The Sci Data paper cites 20260708-001 | RIKEN pages, bioRxiv text |
| Licence | CC BY 4.0 (RIKEN page and SSBD page both say so). The Sci Data article text itself is CC BY-NC-ND (paper only, not the data) | scrape |
| Size | 1.3 TB total. Bundles on SSBD: Processed_Calcium_Data.zip 10.5 GB, EEG_EMG_Data.zip 1.2 GB, Raw_Calcium_Imaging.zip 931.2 GB. For the toolbox you only need the first two (about 11.7 GB) | SSBD repository page |
| Species | Mus musculus, C57BL/6JJmsSlc, both sexes; sleep mice 12-24 wk, anesthesia mice 28-62 wk; G-CaMP7.09 | SSBD + bioRxiv methods |
| Animals | Number of animals UNVERIFIED (paper says per-column Tables S1/S2 map to sessions; no animal count seen) | |
| Sessions | 10 total: 6 wake-sleep sessions + 4 wake-anesthesia sessions. One file per continuous session | bioRxiv Data Records |
| Modality | Wide-field two-photon, layer 2/3, multi-area, 7.65 Hz frame rate. 4,000-10,000 retained neurons per session (detected ROIs 7,571-19,635; retained 4,337-10,197) | Sci Data abstract, bioRxiv |
| Deconvolved? | YES. Per file: `dFF`, `spike_deconv` (OASIS), `spike_smoothed` (Gaussian 1.96 s, 15 frames). Matrices N x T | bioRxiv Data Records / Technical Validation |
| Sleep labels? | YES. `state` vector aligned to frames. Sleep sessions: wakefulness, quiet wakefulness, NREM, REM. Anesthesia sessions: wakefulness, isoflurane. Scored from EEG/EMG with a 4 s sliding window, post hoc. Raw EEG/EMG also shipped (.mat) | same |
| Epoch structure | Wake-sleep sessions: continuous recording of wake then natural sleep. Wake-anesthesia: wake then isoflurane. NO task epoch. REM and quiet wake are rare. Analysis windows 1,500 frames (196 s) for sleep, 2,900 frames (379 s) for anesthesia | bioRxiv Usage Notes |
| Other variables | `ROIs.atlas`, `ROIs.Centroid`, `frame.boundary_ind`, `frame.used_frame`, `data_info`, `animal_info`, optional `nonzero_ROI` | bioRxiv |
| Format | MATLAB .mat (processed + EEG/EMG), TIFF (raw). SSBD lists file types .mat, .md, .xml, .tiff. README with MATLAB and Python loading examples exists (says the paper) | SSBD, bioRxiv |
| File names / keys via API | Not listable. neurodata.riken.jp is a JS single-page app (no API found, 404 on guesses). SSBD folder tree loads on demand: Processed_Calcium_Data = 14 items, EEG_EMG_Data = 12 items, Raw_Calcium_Imaging = 10 items. Exact file names UNVERIFIED. Machine-readable manifests exist: https://ssbd.riken.jp/data/ssbd-000538/zip-manifest.txt, repos-manifest.txt, sha256sum.txt, dataset.json (not fetched) | SSBD downloads page |
| Loader needs | `scipy.io.loadmat` (or `mat73`/h5py if saved as v7.3: UNVERIFIED which). Keys above. State codes (numeric mapping of `state`) UNVERIFIED, read the README |
| Caveats from the authors | Sleep and anesthesia are separate session types; quiet wake and REM rare; atlas labels approximate; ROI set differs per session (QC applied per session) |

Why it is only a weak fit: the toolbox needs "POST sleep vs TASK vs PRE sleep, same cells". Here the best you can do is: wake bout = TASK stand-in, earlier sleep bout = PRE, later sleep bout = POST, all inside one session, so cells are identical by construction. Whether sleep-wake-sleep order exists with enough NREM in each bout is UNVERIFIED and must be checked from the `state` vector of the six sleep files.

## 2. DANDI search (task 2)

Queries run against `api.dandiarchive.org/api/dandisets/?search=...`:
- "sleep": 16 hits. "NREM": 5. "reactivation": 2. "replay": 8. "offline": 11. "consolidation": 5. "REM": 953 (substring noise, useless). "two-photon sleep", "miniscope sleep", "calcium sleep", "calcium imaging sleep", "sleep deprivation": 0 hits each (multi-word search is AND on whole phrase, so it fails).
- Sweep: 530 dandisets pulled via 16 terms (sleep, miniscope, calcium imaging, two-photon, hippocampus calcium, CA1 calcium, 1p calcium, microendoscope, GCaMP, reactivation, consolidation, learning memory imaging, EEG EMG, wake, cortex calcium, ophys); for each I read draft `info` and kept those whose `variableMeasured` has an imaging/ROI type AND whose name/description/keywords match sleep|NREM|REM|slow wave|hypnogram|consolidat|offline|post-learning. Result: ONE dandiset, 000718. (A looser second sweep, text match without the imaging-variable requirement, was still running when this file was written; see addendum at the end.)

Sleep-related hits (all verified present on DANDI) and why they are out:

| Dandiset | Title | Size / files | Modality | Verdict |
|---|---|---|---|---|
| 000718 | Offline ensemble co-reactivation links memories across days | 40.6 GB / 20 files | 1p calcium (OnePhotonSeries, PlaneSegmentation) | See section 2a |
| 000041 | Network Homeostasis and State Dynamics of Neocortical Sleep | 149 GB / 22 | ephys (not calcium; not checked in detail) | out (not calcium) |
| 001695 | High-density extracellular recordings (Neuropixels/SiNAPS) of Hippocampal-Cortical dynamics during s... | 3.1 GB / 22 | ephys | out (not calcium) |
| 000061 | Reactivations of emotional memory in the hippocampus-amygdala system during sleep | 1.95 TB / 40 | ephys (title only; not opened) | out (not calcium) |
| 000044 | Diversity in neural firing dynamics supports both rigid and learned hippocampal sequences | 73 GB / 8 | ephys (not opened) | out (not calcium) |
| 000115, 000629, 000687 | Gillespie 2021 / 2024 replay, interleaved learning | 4.6 GB-17 GB | ephys (rat) | out (not calcium) |
| 001888, 000987, 000939, 000218, 000056, 000166, 000233, 000978, 000065, 001699 | other "sleep"-term hits | various | ephys/EEG | out (not calcium) |

### 2a. DANDI:000718 (checked specifically)

| Field | Result |
|---|---|
| Title | Offline ensemble co-reactivation links memories across days |
| Authors (first / last) | Zaki Y (contact), Pennington ZT, ... Shuman T, Cai DJ. Paper: Nature 2025, doi:10.1038/s41586-024-08168-4 (Europe PMC PMC11666460, CC BY) |
| Licence | CC-BY-4.0 |
| Version | draft; published version 0.260825.1902 exists |
| Size / assets | 40,636,589,615 bytes (40.6 GB), 20 assets (10 .nwb, 10 .wmv behaviour videos, each .wmv 10-23 MB) |
| Species / subjects | Mus musculus; 2 subjects in DANDI (sub-Ca-EEG2-1, sub-Ca-EEG3-4). The paper's EEG experiment reports n = 5 (high-shock) + 4 (low-shock) mice, so DANDI holds only a subset (UNVERIFIED why) |
| Modality | 1p miniscope calcium (dorsal CA1, GCaMP6f). NWB variables: OnePhotonSeries, ImagingPlane, PlaneSegmentation, OpticalChannel, ProcessingModule. No ElectricalSeries / TimeIntervals listed in `variableMeasured` |
| Files | sub-Ca-EEG2-1: ses-FC, ses-NeutralExposure, ses-OfflineDay2Session1, ses-Recall1, ses-Week. sub-Ca-EEG3-4: ses-FC, ses-NeutralExposure, ses-OfflineDay1Session1, ses-OfflineDay2Session1, ses-Recall1/2/3. Each NWB is 2.2-4.7 GB (the OnePhotonSeries raw video is inside, so one file cannot be read cheaply without remote HDF5 access) |
| Deconvolved? | Paper: "calcium transients were then deconvolved ... Deconvolved calcium activities were analysed" (Minian CNMF). Whether deconvolved traces are stored in the NWB: UNVERIFIED (no h5py here to peek) |
| Sleep stages? | In the PAPER: yes. HD-X02 EEG/EMG telemetry, 6 s epochs, automatic GMM wake/NREM/REM, validated against manual scoring, 12 h offline period. In the DANDI NWB: UNVERIFIED and doubtful (no ephys/EEG series declared; the description keywords do not mention EEG) |
| PRE / TASK / POST? | Design is Neutral encoding -> Offline 1 (post-neutral, 12 h with EEG) -> Fear conditioning (aversive encoding) -> Offline 2 -> Recall. So Offline 1 = PRE for the aversive TASK, Offline 2 = POST. Cells are cross-registered with CellReg between each offline and the encoding/recall sessions, NOT among offline sessions ("would lead to too many conflicts"). So PRE-sleep vs POST-sleep from the same cells is not available by design. Cross-registration maps are not visible among the listed DANDI assets |
| Companion data | Paper's "Data availability" points to GitHub denisecailab/RetrospectiveMemoryLinkingData_2024: only figure-panel CSVs + notebooks (no traces). Paper also says the calcium data are available "upon reasonable request" through NWB. Analysis code: github.com/denisecailab/RetrospectiveMemoryLinkingAnalysis_2024 |
| Verdict | Right biology, wrong packaging. Not recommended for a hackathon: 40 GB, 2 subjects, unverified labels, no cross-offline cell identity |

## 3. Other repositories (task 3)

Zenodo `api/records` queries run: sleep calcium imaging; sleep reactivation; two-photon sleep; miniscope sleep; NREM calcium; sleep consolidation imaging; REM sleep calcium. figshare `articles/search` (6 queries): nothing relevant (1 irrelevant hit). OSF `nodes` title search: nothing relevant. Dryad web API not queried directly (Zenodo mirrors Dryad deposits; hits below with doi 10.5061/dryad.* came from that mirror). CRCNS listing page: not checked (UNVERIFIED, not done).

| # | Record | Repo / ID | Licence | Size | Modality | Sleep staging | PRE / TASK / POST same cells | Verdict |
|---|---|---|---|---|---|---|---|---|
| A | Formation of task representations and replay in mouse mPFC (Shabani, Muysers, Yiu, Sauer, Bartos, Leibold; eLife 2026, doi:10.7554/eLife.106981) | G-Node GIN doi:10.12751/g-node.b8k1yn; raw from Muysers 2024 at Zenodo doi:10.5281/zenodo.10528244 | CC BY 4.0 (GIN record). Zenodo raw: cc-by-4.0 | GIN zip 1.4 GiB; Zenodo raw data_and_code.zip 17.4 GB | 1p miniscope calcium (Thy1-GCaMP6f), mPFC, 4 mice (paper: "four Thy1-GCaMP6f mice"; GIN folders list 478, 481, 483, 485, while the paper's figure legend also names 482, so the ID labelling is inconsistent). SECURITY: files are Python pickles, only load after sha/provenance check (np.load allow_pickle=True runs code) | NO stages. Paper states no LFP/EEG in this task; "sleep derived from intermittent sleep epochs" (definition UNVERIFIED) | YES per paper: "recorded during sleep in their homecage before and after learning of the task"; cells tracked across sessions (arena, task, sleep) with CellReg; the paper itself runs a Peyrache 2010 PCA reactivation-strength analysis. Task = M-maze odor task, 3 d arena, 4 d learning, 4 d learned | **Pick** (see ranking) |
| B | REM sleep stabilizes hypothalamic representation of feeding behavior (Oesch et al., PNAS 2020, doi:10.1073/pnas.1921909117) | Dryad doi:10.5061/dryad.kh189323d (Zenodo mirror id 3971091) | CC0 | 8.5 GB single zip (Oesch_et_al_ImagingData.zip); includes mat-files and Matlab scripts per the paper's data statement | Miniscope calcium (CNMF-E), lateral hypothalamus vgat neurons, 5 animals in the feeding analyses, 10 fps | YES: EEG/EMG recorded, REM/NREM/wake; patterns "reactivated during REM, not NREM" | Cells tracked across sessions (CNMF-E on concatenated sessions). Task = free feeding (no learning). Whether a PRE-feeding sleep session exists: UNVERIFIED. Deconvolved: normalized dF/F, no deconvolution stated | Strong fallback on biology (task pattern reactivated in sleep, staged). Not hippocampal/cortical. Large single zip |
| C | Cholinergic modulation of hippocampal calcium activity across the sleep-wake cycle (Dryad doi:10.5061/dryad.8ct101p; Zenodo mirror 4970949) | Dryad | CC0 | 377 MB (Cadata.mat 192 MB, lfpdata.mat 169 MB, positiondata.mat 15 MB) | endoscopic CA1 calcium + LFP | Sleep/wake from LFP (labels not seen in file list) | Exploration + sleep states, but no PRE/TASK/POST design | Only small, quick-to-load "calcium + LFP across states" set. No task structure |
| D | Dynamic changes in cortical NDNF interneurons during sleep (Zenodo 13921467, doi:10.5281/zenodo.13921467) | Zenodo | CC-BY-4.0 | 221 MB (3 .mat: CM2308_m1/m3/m4_Calcium_synched.mat) | miniscope dF/F, V1 L1 NDNF, 48 h, synced with sleep-scored EEG/EMG (description says so) | YES (description) | No task | Small, well-staged sleep calcium. No task/learning. Useful only to test the staging/pre-processing path |
| E | Dataset for Kim et al., Nature 2022 (Zenodo 7226711, doi:10.5281/zenodo.7226711) | Zenodo | CC-BY-4.0 | 77 files, ~10.8 GB (e.g. Animal4_Day10.mat 176 MB) | **ephys (M1/striatum, rats), NOT calcium** | NREM LFP delta etc. | YES: per-day mat = pre-training sleep, reach task, post-training sleep | Perfect PRE/TASK/POST structure but spikes not calcium. Listed because it is the cleanest verified template; does not meet the calcium criterion |
| F | Neural ensemble reactivation in REM and SWS ... rapid motor skill learning (Dryad doi:10.5061/dryad.7d7wm37rn; Zenodo mirror 4992158) | Dryad | CC0 | 6.1 GB, 68 files (.ncs raw, .m scripts, README.txt) | ephys (rat M1 tetrodes), NOT calcium | REM/SWS | pre-task rest, task, post-task | Ephys only. Not calcium |
| G | A cortical-hippocampal communication undergoes rebalancing after new learning (Hall & Wang, eLife 2026; data figshare doi:10.6084/m9.figshare.33467404) | figshare | not checked | not checked | ephys (27 hits for ephys terms, 2 for calcium) | sleep present | learning present | Ephys. figshare record itself not opened |

Papers whose data statements I read and that did not qualify:
- Zaki et al. Nature 2025 (PMC11666460): see 2a.
- Shabani et al. eLife 2026 (PMC12999172): data statement = G-Node doi:10.12751/g-node.b8k1yn + code github.com/HamedShabani/PFC_sequence_analysis; part of the data overlaps Zenodo 10.5281/zenodo.10528243/10528244 (both IDs resolve to the same record "Code & Data for 'A persistent prefrontal reference frame across time and task rules'").
- Oesch PNAS 2020 (PMC7430996): Dryad doi:10.5061/dryad.kh189323d.
- "Replay of procedural memory is independent of the hippocampus" (Nat Neurosci 2026, PMC13533836, data Zenodo doi:10.5281/zenodo.20055819): text hits for calcium are few (3) vs sleep (137); did not open the Zenodo record, so modality UNVERIFIED.
- "Environmental enrichment accelerates the stabilization of cortical representation during de novo learning" (iScience 2026, PMC12805373): calcium imaging, only 5 sleep mentions, no data statement found in text: out.
- "Layer 1 NDNF interneurons ... opposite activation patterns during sleep" (PNAS 2025, PMC12377762): calcium + staged sleep, no task; its data appears to correspond to item D (not confirmed by the statement, I did not read it).

## 4. Ranking against the qualification criteria (task 4)

Legend: Y = verified yes, P = partial/with caveat, N = verified no, ? = UNVERIFIED.

| Criterion | A. G-Node mPFC (Shabani) | RIKEN (named fallback) | B. Oesch LH feeding | DANDI:000718 | E. Kim 2022 (ephys) |
|---|---|---|---|---|---|
| Calcium data | Y (1p, mPFC) | Y (2p, L2/3) | Y (miniscope, LH) | Y (1p, CA1) | N (ephys) |
| Deconvolved / event data | P: thresholded transient trains ("Spike_binary", "extract", 3 sigma, min 0.2 s); not OASIS/CNMF-spikes | Y: `spike_deconv` (OASIS) + `dFF` + smoothed | P: normalized dF/F (deconvolvable) | ? (paper deconvolved; NWB content unverified) | spikes |
| PRE sleep / TASK / POST sleep, same cells | Y per paper (home-cage sleep before and after learning, CellReg across all sessions). Sleep folder lists one file per mouse; whether pre/post are distinguishable inside the file: ? | N by design (no task). Within-session wake bout as TASK stand-in: ? | P: task = free feeding; pre-sleep ? | P: Offline1 -> FC -> Offline2, but registration is offline-vs-encoding only | Y (rat) |
| Sleep stages | N (no EEG/LFP; sleep epochs only) | Y (wake / quiet wake / NREM / REM from EEG/EMG; raw EEG/EMG shipped) | Y (EEG/EMG) | Y in paper, ? in DANDI | Y (LFP delta etc.) |
| Licence | CC BY 4.0 | CC BY 4.0 | CC0 | CC-BY-4.0 | CC-BY-4.0 |
| Download for the toolbox | 1.4 GiB (GIN zip); raw 17.4 GB not needed | ~11.7 GB (Processed 10.5 + EEG/EMG 1.2); skip 931 GB raw | 8.5 GB (one zip) | 40.6 GB (cannot subset cheaply) | ~10.8 GB (77 files), single days 67-176 MB |
| Format / effort to load | Python pickle without extension (`np.load(..., allow_pickle=True)`); dict keys documented in GIN README (`extract`, `Spike_binary`, `seq_mask`, `bursts`, `ids_clust`, `Spike_times_cells`, masks per session/condition). Low effort | .mat (MATLAB), N x T matrices + `state`. Low effort; version of .mat unknown | .mat inside zip. Medium (structure undocumented in what I saw) | NWB 2-5 GB each; needs pynwb/h5py + remote streaming (DANDI). High | .mat per day. Medium |
| Overall | **Best match to the reactivation question (PRE/TASK/POST, same cells, small, Python-native)** but unstaged sleep and only 4 animals | **Best data quality for calcium + staging**, no task | Best "task pattern reappears in staged REM" but non-cortical and 8.5 GB | Not recommended | Template only, fails calcium |

Recommendation:
1. PICK: G-Node PFC_Data (doi:10.12751/g-node.b8k1yn). It is the only verified calcium record whose own paper states same-cell PRE sleep, TASK, POST sleep. Say plainly in the pitch that sleep is unstaged (no NREM/REM). 1.4 GiB, CC BY 4.0, plain-Python loader. The authors' own analysis there (Peyrache-2010 PCA reactivation strength) matches your test.
2. FALLBACK: RIKEN CBS 20260708-001 (doi:10.60178/cbs.20260708-001). Use `spike_deconv` + `state`; define PRE/TASK/POST from a wake bout flanked by two sleep bouts. Check feasibility first from the six sleep files' `state` vectors (see "Not verified" item 3).
3. Plainly: nothing fully qualifies. If you must have staged sleep AND a real task AND calcium, the only verified candidate is Oesch 2020 (Dryad), at the cost of an 8.5 GB zip, non-cortical cells, and an unverified pre-sleep session.

## Not found / could not verify

1. RIKEN exact file names and `.mat` version: neurodata.riken.jp is a JS app with no discoverable API; SSBD folder tree loads on demand. Manifest URLs given above, not fetched. State-code mapping, animal count, and per-session durations (bioRxiv Table 2) not seen.
2. RIKEN: whether any wake-sleep session actually contains sleep-wake-sleep order with enough NREM in both sleep bouts. Must be tested from the `state` vector.
3. G-Node PFC_Data: how "sleep epochs" are defined (no EEG/LFP in this experiment, so presumably behaviour/immobility), whether the Sleep files separate pre-learning vs post-learning, sampling rate of the traces, per-file sizes (individual files not opened). Also not seen: whether the mat/pickle keys listed in the README apply identically to the Sleep files.
4. DANDI:000718: whether the NWB files contain deconvolved events, sleep-state labels, or EEG/EMG; whether cross-registration (CellReg) maps are shipped; why only 2 of 9 mice are in DANDI. No h5py/remfile installed here, so I did not stream-read any NWB.
5. DANDI full-text search returned nothing for two-photon/miniscope/calcium + sleep as phrases (search quirk). My sweep covered 530 dandisets via 16 terms; dandisets with no description text matching sleep terms would be missed.
6. CRCNS dataset listing: not checked. Dryad native API and Dataverse/Mendeley/OpenNeuro: not queried. Allen Institute / IBL: not checked.
7. Oesch 2020: whether a pre-feeding sleep session exists, file structure inside the 8.5 GB zip, frame/sleep epoch layout.
8. Hall & Wang eLife 2026 figshare record, and Nat Neurosci 2026 Zenodo 20055819 record: not opened (modality/licence unknown).
9. A published two-photon dataset from a sleep-learning paper with PRE/TASK/POST + calcium + staged sleep (e.g. from Gan/Li, Peyrache, Lee labs): none turned up in the searches above. Absence is not proof.

## Addendum: looser DANDI sweep (finished)

Same 530 dandisets, text match on sleep terms plus any of calcium|GCaMP|imaging|ophys|miniscope in the text (no imaging-variable requirement). 14 hits: 000041, 000044, 000065, 000166, 000233, 000718, 000939, 000978, 000987, 001177, 001699, 001844, 002013, 002014. All are CC-BY-4.0. Apart from 000718, none declares an imaging series in its asset summary (the earlier strict sweep dropped them), so they are ephys/other records that merely mention imaging or sleep in their text. I did not open their descriptions individually, so "ephys" for 000987, 000978, 001177 is inferred from the absent imaging variables, not read. Conclusion unchanged: 000718 is the only DANDI record with sleep + imaging data.
