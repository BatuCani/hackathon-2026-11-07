# Open electrophysiology datasets for a full reactivation and replay analysis

Scout report, 2026-11-07.
Target analyses: Tingley & Peyrache (2020), Phil. Trans. R. Soc. B 375: 20190231 (EV/REV, PCA/ICA template matching, Bayesian decoding with line fit / Radon / weighted correlation, rank-order, cross-correlation bias, shuffles).

## Summary

- **One dataset fully qualifies on every REQUIRED criterion, verified file by file: Grosmark & Buzsáki 2016, published twice: DANDI:000044 (NWB, CC-BY-4.0, no login) and CRCNS hc-11 (Neuroscope, login).**
  All 8 sessions have PRE 133-322 min / MAZE 34-93 min / POST 133-270 min, 51-137 units (41-120 pyramidal), 39 Hz position, five-state sleep labels plus EMG and accelerometer, and 1250 Hz CA1 LFP on 128 channels.
  The only preprocessing needed is ripple detection; there is no ripple-times table in the NWB files.
- **Best near-miss: DANDI:001695 (Gonzalez & Vöröslakos 2026, Neuropixels 2.0, mouse CA1/CA3 + RSC).**
  It is small (3.1 GB in total), has 110-430 units per session, precomputed ripple times (97-4605 per session) and NREM/REM/WAKE labels.
  Its position tracking is **25 Hz**, which is below the 30 Hz requirement.
  It also has no epoch table (epochs can be recovered from the position timestamps) and no linked paper.
- **Girardeau 2017 (DANDI:000061 = CRCNS hc-14)** has the PRE/RUN/POST design, sleep labels and 1250 Hz LFP.
  The DANDI copy ships only raw video, no position.
  The CRCNS copy has position and ripple `.evt` files, but its tracking rate and per-session counts were not verifiable without a login.
  Across its 34 sessions with units, hippocampal units range from 0 to 83 and reach 50 or more in only 7 sessions.
- **Frank/Jadhav-style W-track data (DANDI:000978, CRCNS hc-6, hc-28)** fails the sleep-duration criterion: its rest epochs last about 15-23 min.
  Peyrache head-direction sets (DANDI:000056, 000939) fail the structured-track / lap criterion (open field) and have few or no CA1 units.
- No IBL or Allen release documents sleep epochs.
- No calcium dataset qualifies as primary data, as required by the task.
- The earlier "RIKEN" calcium recommendation from the sibling reports is outside this ephys scope; I did not re-verify it here.

## Method

- **DANDI:** REST API search (`sleep`, `replay`, `reactivation`, `ripple`, `sharp wave`, `NREM`, `head direction`, `linear track`, `maze`) gave 60 dandisets.
  For each relevant candidate I streamed the NWB HDF5 headers from S3 with `h5py` + `remfile`, with no file download.
  I read `intervals/epochs`, `intervals/trials`, the sleep-state interval tables, the `units` table (count, `cell_type`/`location` columns, spike-time quantisation) and the rates of every TimeSeries.
- **CRCNS:** about pages and the public `crcns_<id>_data_description.pdf` for hc-3, hc-5, hc-6, hc-11, hc-13, hc-14, hc-18, hc-25, hc-28, hc-31, pfc-2, pfc-6 and th-1, plus scans of the hc/pfc/th series lists.
  The data directories need an account, so I did not open per-session files.
- **Dryad / Zenodo / Figshare / GIN / lab sites:** API metadata and file listings.
  Dryad file downloads now return `Unauthorized, must have current bearer token`, so READMEs inside Dryad were not readable.
  The Buzsáki databank is Globus-only, with no public session table.
- Total data transferred: HDF5 header and metadata reads only, well under the per-dataset cap.

## 1. Qualifying datasets

| Dataset name | Repository + URL/DOI | Species/region | Recording method | Sessions (n) | Units per session (range) | PRE/RUN/POST present | Epoch durations | Behaviour type + tracking rate | Sleep labels | Event/LFP data | Second environment | Format | Licence | Associated paper |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Grosmark & Buzsáki 2016, "Diversity in neural firing dynamics supports both rigid and learned hippocampal sequences" | DANDI:000044, https://dandiarchive.org/dandiset/000044/0.261106.0236 , DOI 10.48324/dandi.000044/0.261106.0236 (also CRCNS hc-11, DOI 10.6080/K0862DC5 per CRCNS page https://crcns.org/data-sets/hc/hc-11) | Rat (Long-Evans, 4 animals), bilateral dorsal CA1 | 2 silicon probes, 128 ch, 20 kHz wideband sorted (spike times quantised to 1/20000 s) | 8 | 51-137 total; 41-120 pyramidal (`units.cell_type`) | Yes, `intervals/epochs` labels PRE / MAZE / POST | PRE 179-322 min, MAZE 34-93 min, POST 133-270 min | Novel 1.6 m linear (4 sessions), 2 m metal linear (1), 1 m circular unidirectional (3), per `session_description`; 2D + linearised position at 39.06 Hz; linear sessions have 66-141 directional runs in `intervals/trials` | Yes: `sleep_states` (Wake, Drowsy, NREM, Intermediate, REM) and `sleep_states_buzcode` (WAKE/NREM/REM); NREM 2.1-4.4 h per session | 1250 Hz LFP on 128 CA1 channels, plus neck EMG and 3-axis accelerometer at 1250 Hz; no ripple-time table (detect from LFP) | No (one novel maze per session) | NWB 2.x (HDF5); CRCNS copy is .res/.clu/.eeg/.xml + .mat | CC-BY-4.0 (DANDI); CRCNS: citation conditions, account required | Grosmark & Buzsáki 2016, Science 351:1440, doi:10.1126/science.aad1935; Chen et al. 2016, Sci Rep 6:32193, doi:10.1038/srep32193 |

Per-session values (DANDI:000044, streamed `units` and `intervals/epochs`):

| Session | Units (pyr / int) | PRE / MAZE / POST (min) | Maze | Directional runs (in/out) | NREM (s, lab scoring) |
|---|---|---|---|---|---|
| Achilles 10252013 | 137 (120 / 17) | 301 / 34 / 245 | 1.6 m linear | 92 (49 / 43) | 15488 |
| Achilles 11012013 | 104 (92 / 12) | 322 / 45 / 244 | circular | no trials table | 10620 |
| Buddy 06272013 | 68 (48 / 20) | 179 / 39 / 133 | 1.6 m linear | 66 (31 / 35) | 7580 |
| Cicero 09012014 | 73 (55 / 18) | 259 / 93 / 228 | 1.6 m linear | 141 (64 / 76) | 13168 |
| Cicero 09102014 | 105 (81 / 24) | 287 / 50 / 270 | circular | no trials table | 13901 |
| Cicero 09172014 | 72 (59 / 13) | 267 / 51 / 241 | 2 m metal linear | 106 | not extracted |
| Gatsby 08022013 | 80 (66 / 14) | 285 / 39 / 183 | 1.6 m linear | 86 (44 / 42) | not extracted |
| Gatsby 08282013 | 51 (41 / 10) | 279 / 45 / 265 | circular | no trials table | not extracted |

Evidence (Buddy session, asset `a13eb5ce-89c8-4c21-a5a2-34e00a59ac0f`):

```
INTERVALS intervals/epochs: n=3
   0.0-10717.9 (178.6 min) {'label': 'PRE'}  10717.9-13046.0 (38.8 min) {'label': 'MAZE'}  13046.0-21054.7 (133.5 min) {'label': 'POST'}
UNITS n= 68  cell_type {'interneuron': 20, 'pyramidal cell': 48}   spike time range 0.1083 21054.6546
TS acquisition/accelerometer rate=1250.0   TS acquisition/neck_emg rate=1250.0
TS processing/behavior/position/position_2d rate=39.06 t0=10717.9
INTERVALS processing/behavior/sleep_states: Drowsy 4578s, Intermediate 332s, NREM 7580s, REM 1099s, Wake 6585s
TS processing/ecephys/LFP/lfp data(26318375, 128) rate=1250.0
```

The DANDI description states the stability basis: "All eight sessions were concatenated from the PRE, MAZE, and POST recording epochs".
CRCNS adds: "All spike extraction and clustering was performed on the wideband (20 kHZ) signal".
Units therefore span the whole session; the spike-time ranges cover 0 s to the session end.

## 2. Per-criterion check

Legend: met / met with preprocessing / not met / unverified.

| Criterion | DANDI:000044 / hc-11 | DANDI:001695 | DANDI:000061 / hc-14 | DANDI:000978 | CRCNS hc-25 |
|---|---|---|---|---|---|
| Units N≳50, stable PRE-RUN-POST | met (51-137, sorted on concatenated session) | met (110-430 per behaviour session; CA1 57-219) | met for 7 of 34 sessions on hippocampal units alone (50-83 hpc); total units 40-252 across all regions | met for count (72-240), stability across 17 epochs unverified | unverified |
| ≤1 ms spike timestamps, extracellular | met (20 kHz) | met (30 kHz, Neuropixels 2.0) | met (20 kHz) | met (30 kHz quantisation) | met (.res) |
| PRE + RUN + POST, durations | met | met with preprocessing (no epoch table; from position timestamps: PRE 68-115 min, RUN 24-57 min, POST 60-135 min) | met (presleep 108-238 min, run 14-60 min, postsleep 28-194 min per block; epoch times stored in ms, so divide by 1000) | not met (sleep epochs 15-23 min) | met structurally, durations unverified |
| Position ≥30 Hz, structured track, ≥10-20 laps/direction | met (39 Hz; linear sessions 31-76 runs per direction; circular sessions need lap extraction) | not met (25 Hz; track roughly 1 m by position range, laps unverified) | met with preprocessing on DANDI (only ~30 fps raw video); CRCNS has position files, rate unverified | met (32.5 Hz, W-track, 119-366 trials) | not met (open box with objects) |
| Sleep labels or raw signals | met (labels + EMG + accelerometer) | met (NREM/REM/WAKE intervals) | met (Awake / Non-REM / REM intervals) | met with preprocessing (no labels; 1500 Hz LFP) | unverified |
| LFP ≥1-1.25 kHz in CA1 or event times, 100+ events | met with preprocessing (1250 Hz, 128 CA1 channels; detect ripples) | met (1250 Hz best-ripple channel + 97-4605 precomputed ripples) | met (1250 Hz, 160 ch); CRCNS also has ripple `.evt` | met with preprocessing (1500 Hz) | met with preprocessing (1250 Hz) |
| Optional: second environment | no | some sessions ("Novel or 2-maze configurations", per description); not identified per file | no | no (one W-track; ZT2 has two objects/files) | no |
| Optional: second region | no | yes (RSC 9-201 units per session) | yes (BLA, piriform and others) | yes (PFC, per description) | yes (mPFC) |

## 3. Partial matches (missing one or more REQUIRED criteria)

### Extracellular

- **DANDI:001695**, Gonzalez & Vöröslakos 2026, mouse CA1/CA3/RSC Neuropixels 2.0 (https://dandiarchive.org/dandiset/001695/0.260319.2023, 3.1 GB, CC-BY-4.0, NWB).
  Missing: position tracking is 25 Hz (below 30 Hz); there is no epoch table and no associated paper.
  Otherwise it is the richest set (15 behaviour sessions, 110-430 units, precomputed ripples, sleep labels, cortex).
- **DANDI:000061 / CRCNS hc-14**, Girardeau, Inema & Buzsáki 2017, rat dorsal hippocampus + BLA, silicon probes (https://dandiarchive.org/dandiset/000061/0.250624.0426, 1.95 TB, CC-BY-4.0; https://crcns.org/data-sets/hc/hc-14).
  Missing: hippocampal units reach 50 or more in only 7 of 34 sessions (Rat08 0712/0713/0718, Rat11 0316/0327/0328/0331).
  The DANDI copy has no position (raw video and a `trials` table only), and the CRCNS tracking rate is unverified.
  Within those 7 sessions it meets every other REQUIRED criterion except the tracking rate, which is unverified.
- **DANDI:000978**, Shin & Jadhav 2024, single-day W-track learning, rat CA1 + PFC tetrodes (https://dandiarchive.org/dandiset/000978/0.240511.0307, 323 GB, CC-BY-4.0).
  Missing: the sleep/rest epochs last 15-23 min (17 alternating epochs), well under ~1 h each, and there are no sleep labels.
- **CRCNS hc-25**, Maingret et al. 2016 / Todorova & Zugaro 2019, rat CA1 + mPFC tetrodes, 35 PRE/task/POST sessions (https://crcns.org/data-sets/hc/hc-25).
  Missing: the task is an open box with objects, not a lapped track; sleep labels and durations are unverified.
  Some sleep sessions include ripple-triggered cortical stimulation.
- **CRCNS hc-18**, Drieu, Todorova & Zugaro 2018 (https://crcns.org/data-sets/hc/hc-18).
  Missing: "travel" is passive or active transport on a model train (~15 laps × 2), not free running; tracking rate and units are unverified.
  It does have ~90 min sleep epochs.
- **CRCNS hc-6 / hc-28**, Frank and Jadhav labs, W-track (https://crcns.org/data-sets/hc/hc-6 , https://crcns.org/data-sets/hc/hc-28).
  Missing: rest epochs are short and "sleep means resting in a box and not necessarily sleeping"; the LFP rate is unstated.
  They do have two W-tracks and CA1+PFC (hc-28).
- **CRCNS hc-31**, Rich, Liaw & Lee 2014, 48 m track plus open field, "flanking sleep sessions" (https://crcns.org/data-sets/hc/hc-31).
  Missing (unverified): durations, tracking rate and sleep labels.
- **CRCNS pfc-6**, Peyrache et al. 2009, rat mPFC tetrodes, Y-maze rule learning, SwsPre/SwsPost (https://crcns.org/data-sets/pfc/pfc-6).
  Missing: no hippocampus, no LFP, no ripple times, no continuous position track.
  Note that pfc-2 is Fujisawa 2008, not Peyrache 2009.
- **DANDI:000056 / CRCNS th-1**, Peyrache et al. 2015, mouse anterodorsal thalamus + postsubiculum (https://dandiarchive.org/dandiset/000056).
  Missing: open field rather than a lapped track, and few CA1 units (6 of 62 in Mouse12-120806).
  It has PRE sleep 115 min / open field 37 min / POST sleep 113 min, 39 Hz head direction, SWS/REM labels and a second environment.
- **DANDI:000939**, Duszkiewicz, Skromne Carrasco & Peyrache, mouse postsubiculum head direction (https://dandiarchive.org/dandiset/000939).
  Missing: open field, and no CA1/ripple-region LFP.
  It has home cage 84 min / square 44 min / home cage 101 min / triangle 42 min, 117 units, 100 Hz head direction, nrem/rem/wake labels and accelerometer.
- **Dryad 10.5061/dryad.7d7wm37rn**, Eckert, McNaughton & Tatsuno 2020, rat M1 tetrodes, sleep / reach training / sleep, CC0, 6.07 GB.
  Missing: a single recording, a reaching task rather than a track, and spike sorting unverified (`.ntt` files).
- **Dryad 10.7272/Q6KK9927**, Lemke et al. 2021, rat corticostriatal reach learning, CC0, 108 GB.
  Missing: no track; PRE/POST structure and units unverified.
- **MRC BNDU dataset 53**, Dupret lab, mouse DG/CA3/CA1 tetrodes, CC BY-SA 4.0, login required (https://data.mrc.ox.ac.uk/data-set/53).
  Missing: open arenas rather than a track, one mouse, and no LFP files listed.
  It does have SWR event times.
- **Zenodo 5587779**, Denovellis et al. (Frank lab), CC0.
  Missing: interleaved short rest epochs (sleep ≥1 h unverified, likely not met).
- **IBL and Allen Visual Coding Neuropixels.**
  Missing: no sleep epochs documented (IBL passive protocol = spontaneous / RF mapping / task replay; Allen VC = ~3 h head-fixed visual stimuli).

### Calcium imaging (not primary data by rule)

- **DANDI:000718**, Zaki et al. 2025, CA1 miniscope with offline sessions and EEG/EMG.
  Missing: imaging, not ≤1 ms spikes.
  Its contents are as reported by the sibling DANDI scout; I did not re-verify them here.
- **Dryad 10.5061/dryad.jh9w0vt7q / Zenodo 5131509**, Mao & McNaughton, RSC two-photon, rest before and after treadmill running.
  Missing: imaging; rest is immobility, not scored sleep.

## 4. Ranked recommendation

1. **DANDI:000044 (Grosmark & Buzsáki 2016).** It is the only dataset with every REQUIRED field verified in the files themselves, including 2-5 h PRE and POST sleep with five-state labels, 35-90 min of novel-track running at 39 Hz, 51-137 sorted CA1 units and 1250 Hz LFP, all in streamable CC-BY NWB. It is also the canonical replay benchmark: Grosmark & Buzsáki 2016 and Chen et al. 2016 used these exact recordings.
2. **CRCNS hc-11.** This is the same recordings in Neuroscope `.res/.clu` + `.mat` form. Use it if you want the original lab files or the per-session `.mat` (it needs a CRCNS account). It is not an independent second dataset.
3. **DANDI:001695 (Gonzalez & Vöröslakos 2026).** It is the best second dataset: Neuropixels yields 2-4× more units, it comes with ripple times and sleep labels, and it has RSC as a second region. All 22 files total only 3.1 GB. The cost is 25 Hz tracking and epochs that must be recovered from position timestamps.
4. **DANDI:000061 / CRCNS hc-14 (Girardeau 2017).** PRE / run / POST is verified, and an aversive-direction contrast tests experience specificity across running directions. Use only the 7 sessions with 50 or more hippocampal units, and take position and ripple `.evt` from CRCNS.
5. **CRCNS hc-25 (Zugaro lab).** It has 35 PRE/task/POST sessions with CA1 + mPFC, which suits EV/REV and assembly analyses across regions. It is weaker for Bayesian sequence decoding because the task is an open box.

What should ship: a loader that targets DANDI:000044 first (streaming via `remfile`/`fsspec`).
It should read `intervals/epochs` for PRE/MAZE/POST, `processing/behavior/sleep_states` for NREM, and `units` filtered on `cell_type == 'pyramidal cell'`, and it should detect ripples from `processing/ecephys/LFP/lfp`.
DANDI:001695 is the second target, because it already ships ripple times.

## 5. Sources

- Tingley & Peyrache 2020: https://doi.org/10.1098/rstb.2019.0231
- DANDI:000044: https://dandiarchive.org/dandiset/000044/0.261106.0236 (API: https://api.dandiarchive.org/api/dandisets/000044/versions/0.261106.0236/)
- DANDI:001695: https://dandiarchive.org/dandiset/001695/0.260319.2023
- DANDI:000061: https://dandiarchive.org/dandiset/000061/0.250624.0426
- DANDI:000978: https://dandiarchive.org/dandiset/000978/0.240511.0307
- DANDI:000056: https://dandiarchive.org/dandiset/000056/0.261106.1949
- DANDI:000939: https://dandiarchive.org/dandiset/000939/0.261016.2310
- DANDI:000041 (Watson 2016, sleep only, no task): https://dandiarchive.org/dandiset/000041/0.261104.0300
- DANDI:000115 / 000629 (Gillespie, Frank lab; no Units table listed in `variableMeasured`): https://dandiarchive.org/dandiset/000115 , https://dandiarchive.org/dandiset/000629
- CRCNS hc-11: https://crcns.org/data-sets/hc/hc-11/about-hc-11 , https://crcns.org/files/data/hc-11/crcns_hc-11_data_description.pdf
- CRCNS hc-14: https://crcns.org/data-sets/hc/hc-14/about-hc-14 , https://crcns.org/files/data/hc-14/crcns_hc-14_data_description.pdf
- CRCNS hc-25: https://crcns.org/data-sets/hc/hc-25/about-hc-25 , https://crcns.org/files/data/hc-25/crcns_hc-25_data_description.pdf
- CRCNS hc-18: https://crcns.org/data-sets/hc/hc-18/about-hc-18
- CRCNS hc-6: https://crcns.org/files/data/hc-6/crcns_hc-6_data_description.pdf
- CRCNS hc-28: https://crcns.org/data-sets/hc/hc-28/about-hc-28
- CRCNS hc-31: https://crcns.org/data-sets/hc/hc-31/about-hc-31
- CRCNS pfc-6: https://crcns.org/data-sets/pfc/pfc-6/about-pfc-6 ; pfc-2: https://crcns.org/data-sets/pfc/pfc-2/about-pfc-2
- CRCNS th-1: https://crcns.org/data-sets/thalamus/th-1/about-th-1
- Dryad Eckert et al.: https://doi.org/10.5061/dryad.7d7wm37rn ; Dryad Lemke et al.: https://doi.org/10.7272/Q6KK9927
- MRC BNDU dataset 53: https://data.mrc.ox.ac.uk/data-set/53
- Zenodo 5587779 (Denovellis): https://doi.org/10.7272/Q61N7ZC3
- Buzsáki databank: https://buzsakilab.com/wp/database/
- IBL passive protocol: https://docs.internationalbrainlab.org/notebooks_external/loading_passive_data.html
- Allen Visual Coding Neuropixels: https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html

## Not verified / limits

- 000044: ripple counts are not precomputed. NREM totals of 2.1-4.4 h per session make 100+ events near certain, but the count is not verified.
  Lap counts for the 3 circular sessions need extraction from linearised position.
  NREM totals for the last 3 sessions were not extracted.
- hc-11 total size and the per-session `HC-11_Recording_Summary.pdf` sit behind the CRCNS login.
- 000061: the units tables of all 40 files were read (6 files have no units). Position rate and ripple counts were not checked, because they are in the CRCNS copy only.
- 001695: the maze type per session and the "2-maze" sessions were not identified; the epoch bounds are inferred from the first and last position timestamps.
- Dryad READMEs are unreadable without a bearer token; CRCNS per-session files need login.
- Buzsáki databank, Pfeiffer, Foster, Wilson, Dragoi and Csicsvari: no public PRE/RUN/POST spike dataset was confirmed in the time box, so none is reported.
