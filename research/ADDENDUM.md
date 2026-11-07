# Addendum to SOURCES_CAPSULE.md / RESEARCH_CAPSULE.md

Lookups run 2026-11-07 in this session: Firecrawl research search (Europe PMC / bioRxiv / arXiv index), Europe PMC REST via curl, GitHub REST API via curl (unauthenticated), PyPI JSON API, anaconda.org API, DANDI API, Zenodo API.
Rules followed: an item appears only if a lookup returned it. Notes come only from the abstract / metadata / README / source file I saw. I did not read full texts. Items already in the earlier capsules are not repeated, except where marked "(in capsule)" to say why they matter for a new topic.
"pushed" for GitHub = `pushed_at` from the API (can reflect any branch), not strictly last commit on the default branch.

---------------------------------------------------------------------------------

## 1. Rate-preserving / surrogate / shuffle controls, false-positive behaviour

| # | Title | Authors | Year | Venue | ID | Note (from abstract only) |
|---|---|---|---|---|---|---|
| 1.1 | Progress and issues in second-order analysis of hippocampal replay | van der Meer MAA, Kemere C, Diba K | 2020 | Phil Trans R Soc B | doi:10.1098/rstb.2019.0238, PMC7209917 (not OA per EPMC) | Says the main methodological challenge of "first-order" analyses (is SWR content different from chance) is constructing and interpreting different chance distributions; "second-order" analyses compare content across time points/templates (e.g. replay = experience dependence). Same Phil Trans issue as the anchor paper. |
| 1.2 | Comparing Surrogates to Evaluate Precisely Timed Higher-Order Spike Correlations | Stella A, Bouss P, Palm G, Grun S | 2022 | eNeuro | doi:10.1523/eneuro.0505-21.2022, PMC9186111 (CC BY) | Surrogates = implementing a null hypothesis; challenge is to build the null while not altering single-spike-train statistics. Compares uniform dithering with five similar surrogate techniques for detecting significant spatiotemporal patterns. https://pmc.ncbi.nlm.nih.gov/articles/PMC9186111/ |
| 1.3 | Surrogate spike train generation through dithering in operational time | Louis S, Gerstein GL, Grun S, Diesmann M | 2010 | Front Comput Neurosci | doi:10.3389/fncom.2010.00127, PMC2972681 (OA) | Proposes two surrogate methods that conserve both firing rate and ISI statistics with high accuracy; states these are the two most important features to conserve. |
| 1.4 | Spike-Centered Jitter Can Mistake Temporal Structure | Platkiewicz J, Stark E, Amarasingham A | 2017 | Neural Computation | doi:10.1162/neco_a_00927, PMC5955204 (not OA per EPMC) | Interval jitter gives an exact hypothesis test for processes with no temporal structure; spike-centered jitter can give exaggerated false-positive rates (explicit examples). Matlab code: github.com/aamarasingham/bjitter (GPL-3.0, pushed 2017-03-24, README ties it to this paper). |
| 1.5 | Conditional modeling and the jitter method of spike resampling | Amarasingham A, Harrison MT, Hatsopoulos NG, Geman S | 2012 | J Neurophysiol | doi:10.1152/jn.00633.2011, PMC3349623 (not OA per EPMC) | Statistical framing of jitter resampling: what inferences are valid about fine-temporal structure without full control of presynaptic inputs (abstract seen only in part). |
| 1.6 | SpiSeMe: A multi-language package for spike train surrogate generation | Perinelli A, Castelluzzo M, Minati L, Ricci L | 2020 | Chaos | doi:10.1063/5.0011328 (no PMCID returned) | Package for generating spike-train surrogates used for surrogate-based hypothesis testing (abstract seen only in part; I did not locate its repo or licence). |
| 1.7 | A novel, jitter-based method for detecting and measuring spike synchrony and quantifying temporal firing precision | Agmon A | 2012 | Neural Syst Circuits | doi:10.1186/2042-1001-2-5, PMC3423071 (CC BY) | Jitter-based synchrony measure; abstract frames the lack of a well-normalised, robust measure (seen in part). |
| 1.8 | Methodological Caveats in the Detection of Coordinated Replay between Place Cells and Grid Cells (in capsule) | Trimper JB et al | 2017 | Front Syst Neurosci | doi:10.3389/fnsys.2017.00057, PMC5539192 | Re-confirmed in this session: for some analysis methods, coordinated replay was spuriously detected in a significant proportion of randomly matched epochs; stricter evaluation and minimum spike counts reduced this. Still the best "false positive rate of replay shuffles" item found. |

Practical pointers found in code (verified in source files, see topic 5): `elephant.spike_train_surrogates` and `pynapple.process.randomize`.

Count: 7 new + 1 re-confirmed.

---------------------------------------------------------------------------------

## 1b. Firing-rate bias in reactivation / pair-correlation (the anchor paper's first flagged gap)

| # | Title | Authors | Year | Venue | ID | Note (from abstract/snippet only) |
|---|---|---|---|---|---|---|
| 1b.1 | Firing rate modulation: a simple statistical view of memory trace reactivation | Battaglia FP, Sutherland GR, Cowen SL, McNaughton BL, Harris KD | 2005 | Neural Netw | doi:10.1016/j.neunet.2005.08.011 (no PMCID) | Snippet: in some conditions, firing-rate reactivation covaries with reactivation of cell-pair cross-correlations, suggesting both reflect similar processes; primed attractors more likely to activate in subsequent sleep. Only a fragment of the abstract was returned. |
| 1b.2 | A binless correlation measure reduces the variability of memory reactivation estimates | Kruskal PB, Stanis JJ, McNaughton BL, Thomas PJ | 2007 | Stat Med | doi:10.1002/sim.2946 (no PMCID) | Standard Pearson correlation on binned spike counts introduces quantisation noise from arbitrary bin boundaries; small changes in bin width/shift of boundaries change estimates. Directly relevant to the bin-size gap too. |
| 1b.3 | Sequential Reinstatement of Neocortical Activity during Slow Oscillations Depends on Cells' Global Activity | Peyrache A, Benchenane K, Khamassi M, Wiener SI, Battaglia FP | 2010 (Front Syst Neurosci; DOI shows 2009) | Front Syst Neurosci | doi:10.3389/neuro.06.018.2009, PMC2805426 (OA) | Snippet: a latency effect is explained by a simple homogeneous Poisson firing model with sleep-averaged firing rates as parameters, i.e. firing rate alone can produce the sequence effect. |
| 1b.4 | Hippocampal information processing across sleep/wake cycles | Mizuseki K, Miyawaki H | 2017 | Neurosci Res | doi:10.1016/j.neures.2017.04.018 (no PMCID) | Snippet: firing rates of the same neurons are positively correlated across brain states and environments, suggesting memory allocated in preconfigured, skewed networks. Relevant to the lognormal-rate gap. |
| 1b.5 | Acetylcholine-gated current translates wake neuronal firing rate information into a spike timing-based code in Non-REM sleep... | Skilling QM et al | 2021 | PLoS Comput Biol | doi:10.1371/journal.pcbi.1009424, PMC8483332 (OA) | Model + mouse hippocampal recordings: relative firing order among neurons in NREM reflects their relative wake firing rates. Another route by which rate can masquerade as sequence. |
| 1b.6 | Firing rates of hippocampal neurons are preserved during subsequent sleep episodes and modified by novel awake experience | Hirase H, Leinekugel X, Czurko A, Csicsvari J, Buzsaki G | 2001 | PNAS | doi:10.1073/pnas.161274398, PMC55430 | Snippet: in a familiar environment, CA1 pyramidal firing rates are preserved across sleep (abstract cut off). |

Count: 6. No paper found that systematically compares rate-matched shuffles for replay (see "Not found").

---------------------------------------------------------------------------------

## 2. Time-bin size / temporal resolution effects

| # | Title | Authors | Year | Venue | ID | Note |
|---|---|---|---|---|---|---|
| 2.1 | A binless correlation measure reduces the variability of memory reactivation estimates | Kruskal PB et al | 2007 | Stat Med | doi:10.1002/sim.2946 | See 1b.2. Bin width and bin-boundary position change pairwise-correlation reactivation estimates. |
| 2.2 | Temporal resolution shapes inferred higher-order interactions and information representation in neural population activity | Jangjoo F | 2026 | PLoS ONE | doi:10.1371/journal.pone.0322347, PMC13705606 (CC BY) | 23 grid-cell recordings (MEC): at intermediate resolution (order 100 ms) inferred model captures higher-order dependencies plus efficient information representation; finest and coarsest resolutions give poor representation. Not hippocampal replay, but a bin-size sweep method. |
| 2.3 | Optimal decoding of neural dynamics occurs at mesoscale spatial and temporal resolutions | Samiei T, Zou Z, Imani M, Nozari E | 2024 | Front Cell Neurosci | doi:10.3389/fncel.2024.1287123, PMC10899419 (CC BY) | Allen Neuropixels visual-coding mice: decoding accuracy peaked at ~125 ms bins for most subjects; optimum varied by region. Decoding, not replay. |
| 2.4 | On the optimal temporal resolution for information representation in neural activity: a theoretical analysis | Ahmed HF, Samiei T, Nozari E | 2026 | Front Comput Neurosci | doi:10.3389/fncom.2026.1885975, PMC13538443 (OA) | Closed-form d-prime vs temporal scale as function of signal/noise autocorrelation; says it explains when binning/smoothing enhances or degrades decodability. |
| 2.5 | Cell assemblies at multiple time scales with arbitrary lag constellations | Russo E, Durstewitz D | 2017 | eLife | doi:10.7554/eLife.19428, PMC5226654 (CC BY) | Assembly-detection method (CAD) that works at multiple temporal scales, from synchrony to rate co-modulation; abstract states the lack of tools for arbitrary lags and multiple scales. Code in topic 4/5. |
| 2.6 | Organization of cell assemblies in the hippocampus | Harris KD, Csicsvari J, Hirase H, Dragoi G, Buzsaki G | 2003 | Nature | doi:10.1038/nature01834 (no PMCID) | Snippet: the window in which spike times are best predicted from peer activity is 10-30 ms, suggesting assembly synchrony at this timescale. Useful prior for bin-size sweeps. |
| 2.7 | Detection of syntonies between multiple spike trains using a coarse-grain binarization of spike count distributions | Del Prete V, Martignon L, Villa AEP | 2004 | (journal not shown) | PMID:15022842 | Snippet: some assemblies robust across time lengths, others only at delimited resolutions; sample size too small for unbiased estimate of all interactions. Journal and DOI not returned; low priority. |
| 2.8 | Optimizing time histograms for non-Poissonian spike trains | Omi T, Shinomoto S | 2011 | Neural Comput | doi:10.1162/NECO_a_00213 | Histogram shape critically depends on bin size; proposes an optimisation. Generic (not replay). |

Already in the earlier capsule and still the only replay-specific bin-size items I saw: Chen et al 2016 (Sci Rep, bin size/firing rate/neuron count affect reliability) and Box et al 2016 (HMM, accuracy at high temporal resolution and small samples, abstract confirmed again).

Count: 8 new (3 directly on assemblies/reactivation: 2.1, 2.5, 2.6; rest generic neural-population).

---------------------------------------------------------------------------------

## 3. Preplay vs replay controversy and null-model critiques

| # | Title | Authors | Year | Venue | ID | Note |
|---|---|---|---|---|---|---|
| 3.1 | Trajectory events across hippocampal place cells require previous experience | Silva D, Feng T, Foster DJ | 2015 | Nat Neurosci | doi:10.1038/nn.4151, PMC6095134 (OA) | Snippet: the standard interpretation of replay has been challenged by reports of preplay; this paper is the counter-position (title: trajectory events require previous experience). Abstract cut off. |
| 3.2 | Preplay of future place cell sequences by hippocampal cellular assemblies | Dragoi G, Tonegawa S | 2011 | Nature | doi:10.1038/nature09633, PMC3104398 | Snippet: calls the phenomenon preplay; occurred in disjunction with replay of a familiar experience. The founding preplay claim. |
| 3.3 | Preconfigured patterns are the primary driver of offline multi-neuronal sequence replay | Liu K, Sibille J, Dragoi G | 2019 | Hippocampus | doi:10.1002/hipo.23034, PMC6793999 | Abstract frames spontaneous ensemble activity as preconfigured dynamics plus experience-driven patterns; title states preconfigured patterns dominate. |
| 3.4 | Hippocampal place cells construct reward related sequences through unexplored space | Olafsdottir HF, Barry C, Saleem AB, Hassabis D, Spiers HJ | 2015 | eLife | doi:10.7554/eLife.06063, PMC4479790 (OA) | Off-line pre-activation of place-cell sequences for a viewed but unvisited, rewarded part of the environment; not seen for an unrewarded part. Goal-biased preplay. |
| 3.5 | A computational model for preplay in the hippocampus | Azizi AH, Wiskott L, Cheng S | 2013 | Front Comput Neurosci | doi:10.3389/fncom.2013.00161, PMC3824291 (OA) | Model: significant correlations with a new chart arise less often, from random correlations between place-field orderings in the new vs a pre-existing chart. Direct chance-correlation argument for apparent preplay. |
| 3.6 | Intrinsic dynamics of randomly clustered networks generate place fields and preplay of novel environments | Breffle J, Germaine H, Shin JD, Jadhav SP, Miller P | 2024 | eLife | doi:10.7554/eLife.93981, PMC11488848 (OA) | Model of preplay from random clustered connectivity; applies the same place-field and preplay analyses to previously published rat data. |
| 3.7 | Drift-diffusion dynamics of hippocampal replay (in capsule) | Wu Z, Wei X-X | 2026 | PLoS Comput Biol | doi:10.1371/journal.pcbi.1014761, PMC13614660 | Abstract: <1% of SWR events show sequential structure at 100 ms timescale before spatial experience; says preplay coordination is much weaker than after experience; says existing analysis methods give inconsistent metrics. Bioarxiv version 10.1101/2025.10.14.682470. |
| 3.8 | A statistical note on the detection of autoassociative dynamics in hippocampal place-cell sequences | Goenner L, Vitay J, Hamker FH | 2018 | bioRxiv preprint (not peer reviewed as far as seen) | doi:10.1101/365239 | Abstract: a previous step-size decoding approach is prone to a decoding artefact; proposes a modified approach. A concrete statistical-pitfall example. |
| 3.9 | Reactivation, replay, and preplay: how it might all fit together | Buhry L, Azizi AH, Cheng S | 2011 | Comput Intell Neurosci (journal not shown in result; DOI 10.1155/2011/203462) | PMC3171894 | Review; proposes a framework for offline sequential activity incl. preplay and never-experienced trajectories. |
| 3.10 | Strengthened Temporal Coordination within Pre-existing Sequential Cell Assemblies Supports Trajectory Replay | Farooq U, Sibille J, Liu K, Dragoi G | 2019 | Neuron | doi:10.1016/j.neuron.2019.05.040, PMC7197404 | Abstract frames equivocal proposals on de novo creation vs pre-existing sequences underlying trajectory learning (cut off). |

Plus 1.1 (van der Meer 2020: chance distributions, preplay as first-order analysis) and 1.8 (Trimper 2017).

Count: 10 new (+2 cross-listed). Honest caveat: I did not find a paper that directly re-tests preplay significance claims with a new null model beyond the model-based 3.5/3.6/3.7 and the review 1.1.

---------------------------------------------------------------------------------

## 4. Reactivation / replay beyond hippocampus; assembly tools with code

### 4a. Papers (non-hippocampal or calcium imaging)

| # | Title | Authors | Year | Venue | ID | Note |
|---|---|---|---|---|---|---|
| 4a.1 | Reactivation predicts the consolidation of unbiased long-term cognitive maps | Grosmark AD, Sparks FT, Davis MJ, Losonczy A | 2021 | Nat Neurosci | doi:10.1038/s41593-021-00920-7 (bioRxiv 10.1101/2020.08.20.259879) | Calcium-imaging-era study of offline reactivation and consolidation of cognitive maps (abstract fragment; imaging modality not stated in the part I saw). |
| 4a.2 | Cortical reactivations predict future sensory responses | Nguyen ND, Lutas A, Amsalem O, Fernando J, ... Andermann ML | 2024 | Nature | doi:10.1038/s41586-023-06810-1, PMC11014741 | Abstract: patterns of neurons activated by a sensory experience are thought to be reactivated; evoked patterns drift (abstract cut off). Cortical reactivation. |
| 4a.3 | Cortical Reactivation of Non-Spatial and Spatial Memory Representations Coordinate with Hippocampus to Form a Memory Dialogue | Chang H, Esteves IM, Neumann AR, Mohajerani MH, McNaughton BL | 2023 | Nat Commun | doi:10.1038/s41467-023-43254-7, PMC10682454 (OA) | Cortical reactivation coordinated with hippocampal replay (abstract cut off). |
| 4a.4 | Offline orbitofrontal cortex reactivation depends on recency of place-reward changes and coheres with hippocampal replay | Rusu SI et al | 2024 | iScience | doi:10.1016/j.isci.2024.109205, PMC10933476 (OA) | Orbitofrontal offline replay on a maze; replay strength correlates with overnight behavioural change; coordinated with hippocampal replay only in a high-excitability cortical state. |
| 4a.5 | Patterned activation of action potential patterns during offline states in the neocortex: replay and non-replay | Liu T-Y, Watson BO | 2020 | Phil Trans R Soc B | doi:10.1098/rstb.2019.0233, PMC7209911 (OA) | Review of patterned neocortical spiking offline; same issue as the anchor paper. |
| 4a.6 | Temporally delayed linear modelling (TDLM) measures replay in both animals and humans | Liu Y, Dolan RJ, Higgins C, ..., Behrens TE | 2021 | eLife | doi:10.7554/eLife.66917, PMC8318595 (OA) | Domain-general sequence detection toolkit "designed to take care of confounds"; can be extended to rodent replay. I did not verify a code repository. |
| 4a.7 | Awake hippocampal reactivations project onto orthogonal neuronal assemblies | Malvache A, Reichinnek S, Villette V, Haimerl C, Cossart R | 2016 | Science | doi:10.1126/science.aaf3319 | Abstract fragment: chained activation of assemblies during population bursts. Modality not stated in the fragment. |
| 4a.8 | Synfire chains and cortical songs: temporal modules of cortical activity | Ikegaya Y, Aaron G, Cossart R, ... Yuste R | 2004 | Science | doi:10.1126/science.1093173 | Snippet: higher-order sequences are replayed with compressed timing (cortical slices / in vivo; abstract cut off). Historical. |
| 4a.9 | Generative replay across hippocampal-neocortical circuits | Shearer CM, ..., Dupret D, Barron HC | 2026 | bioRxiv preprint (not peer reviewed as far as seen) | doi:10.64898/2026.07.24.740539 | Simultaneous electrophysiology + calcium imaging in mice; V1 neuronal sequences encode relations never experienced; V1 generative replay is predicted by preceding hippocampal activity. |

### 4b. Assembly / sequence detection with code (all lookups returned the repo; licence = GitHub API `license` field)

| # | Tool | Paper (verified) | Lang | Licence | Last push | Note |
|---|---|---|---|---|---|---|
| 4b.1 | github.com/tortlab/Cell-Assembly-Detection | Lopes-dos-Santos V, Ribeiro S, Tort ABL (2013) *Detecting cell assemblies in large neuronal populations*, J Neurosci Methods, doi:10.1016/j.jneumeth.2013.04.010 (README cites it) | MATLAB | none detected by API | 2020-03-26 | Review of three linear (PCA/ICA) methods per abstract. No licence file detected: check before reuse. |
| 4b.2 | github.com/DurstewitzLab/Cell-Assembly-Detection | Russo & Durstewitz 2017 eLife, doi:10.7554/eLife.19428 (CADopti README links it) | MATLAB | none detected by API | 2020-12-13 | Original CAD code. |
| 4b.3 | github.com/DurstewitzLab/CADopti | extension of CAD (README) | MATLAB | GPL-3.0 | 2020-04-11 | Returns per assembly the configuration of maximal temporal coordination across time scales. |
| 4b.4 | Elephant `elephant/cell_assembly_detection.py` | module docstring: implements CAD, cites Russo 2017 | Python | BSD-3-Clause | pushed 2026-11-03 | Python route to CAD; takes binned spike trains at a chosen bin_size. |
| 4b.5 | github.com/EKirschbaum/LeMoNADe | Kirschbaum E et al (2019) LeMoNADe, ICLR (README) | Python (PyTorch) | none detected | 2020-04-02 | Motif/assembly detection in calcium imaging videos. |
| 4b.6 | github.com/darikoneil/gseqNMF | (seqNMF family; paper not checked here) | Python | MIT | 2026-03-01 | Description returned: sequential NMF "with sklearn syntax". Other seqNMF repos are in capsule. |
| 4b.7 | Picado-Muino D, Borgelt C, Berger D, Gerstein G, Grun S (2013) *Finding neural assemblies with frequent item set mining*, Front Neuroinform, doi:10.3389/fninf.2013.00009, PMC3668274 | itself | n/a | n/a | n/a | Abstract: multiple testing is a core challenge of assembly detection; method shifts testing from specific assemblies to patterns of a given size to limit false discoveries. Code link not verified (Elephant ships `spade.py`, which I only saw as a filename). |
| 4b.8 | github.com/Eden-Kramer-Lab/replay_identification | none (README: state-space model combining movement, LFP and ensemble spikes to identify replay) | Python | MIT | 2022-10-29 | README says "still in production and prepublication"; Zenodo DOI badge present. |

Count: 9 papers (4a) + 8 tools (4b).

---------------------------------------------------------------------------------

## 5. pip / conda installable packages (PyPI JSON + GitHub API checked 2026-11-07)

| Package | PyPI ver / upload | Licence (PyPI / GitHub) | GitHub last push | Useful here because (from source files / README seen) |
|---|---|---|---|---|
| elephant | 1.2.1 / 2026-06-10 | BSD-3-Clause | 2026-11-03 | `spike_train_surrogates.py` lists dither_spikes, randomise_spikes, shuffle_isis, dither_spike_train, jitter_spikes, bin_shuffling, trial_shifting, `surrogates()`; also `spade.py`, `cell_assembly_detection.py`, `unitary_event_analysis.py`. conda-forge: NOT found under this name. |
| pynapple | 0.11.4 / 2026-08-20 | MIT | 2026-11-06 | `process/randomize.py`: shift_timestamps, shuffle_ts_intervals, jitter_timestamps, resample_timestamps; `process/decoding.py`: decode_bayes, decode_template, decode_1d, decode_2d; correlograms. conda-forge: NOT found. |
| spikeinterface | 0.105.4 / 2026-10-27 | MIT (GitHub; PyPI licence fields empty) | 2026-11-06 | Spike-sorting/IO framework. conda-forge: found, MIT. |
| neuroconv | 0.10.2 / 2026-09-10 | BSD-3-Clause | 2026-11-06 | Converts proprietary formats to NWB. conda-forge: not found. |
| pynwb | 4.2.0 / 2026-09-02 | BSD-3-Clause on PyPI; GitHub API says NOASSERTION (custom licence file) | 2026-11-04 | Read/write NWB, the format DANDI uses. conda-forge: found, BSD-3-Clause. |
| dandi (client) | 0.82.0 / 2026-11-03 | Apache-2.0 | n/c | CLI/API for DANDI; conda-forge 0.81.0. |
| ripple-detection | 1.7.1 / 2026-01-22 | MIT | 2026-11-01 (Eden-Kramer-Lab/ripple_detection) | Detects 150-250 Hz SWRs from LFP. conda-forge: not found. |
| neo | 0.14.6 / 2026-10-15 | BSD-3-Clause | n/c | Electrophysiology data representation + IO (Elephant's data model). conda-forge: not found under "neo". |
| nelpy (in capsule) | 0.2.1 / **2019-02-07** | MIT | per capsule 2026-10-14 | PyPI release is 2019: install from GitHub for current code. |
| non-local-detector (in capsule) | 0.6.9 / **2024-11-21** | MIT (GitHub) | 2026-11-07 | PyPI lags the repo by ~2 years: install from GitHub. |
| replay-trajectory-classification (in capsule) | 1.4.1 / **2024-09-06** | MIT (GitHub) | 2025-09-26 | PyPI release older than the last repo push. |

Count: 8 new + 3 re-checked. Not on PyPI as far as I looked: `pynacollada`, `cell-assembly` (404 / no `info`). RnR_methods: GPL-3.0 (GitHub API), MATLAB, last push 2021-05-08.

---------------------------------------------------------------------------------

## 6. Open datasets reachable without registration

Checked: DANDI API (`/api/dandisets/?search=...`, `/versions/draft/info/`, `/assets/`), Zenodo API. All DANDI items below report `embargo_status: OPEN`, licence `spdx:CC-BY-4.0`, NWB format. I downloaded nothing (all files are far above 5 MB).

### 6a. DANDI

| ID | Title | Size / assets | Species, n | Has spikes? behaviour? sleep? | Note |
|---|---|---|---|---|---|
| **DANDI:000044** | Diversity in neural firing dynamics supports both rigid and learned hippocampal sequences (Grosmark & Buzsaki) | 73.4 GB, 8 NWB files (5.4-10.4 GB each) | Rattus norvegicus, 4 rats, 8 sessions | Units + LFP + Position: yes. PRE sleep (~4 h) / novel MAZE run (~45 min) / POST sleep (~4 h) concatenated per session: yes | Description text matches CRCNS hc-11 ("eight bilateral silicon-probe recordings from four Long-Evans rats") that the earlier capsule lists as needing a CRCNS account. This is a no-registration route. https://dandiarchive.org/dandiset/000044/draft. The dandiset's published-version field returned version 0.261106.0236; listing says published. Files include raw ElectricalSeries, so stream only Units (do not full-download). |
| DANDI:000978 | Single Day W-Track Learning | 323 GB, 9 NWB (28-47 GB each) | Rattus norvegicus, 8 | Description: position, spike times for dorsal CA1 and prefrontal units, LFP; 8 behavioural sessions interleaved with sleep (17 epochs): yes | Two-region, multi-session sleep/run design. |
| DANDI:000115 | Gillespie et al (2021) Hippocampal replay reflects specific past experiences rather than a plan for subsequent choice | 9.1 TB, 57 assets | Rat, 4 | CA1 tetrodes: ElectricalSeries, Position, behavioural events (description: electrophysiological + behavioural); sleep not stated in description; spike units not listed in variableMeasured | Companion to 000629. |
| DANDI:000629 | Gillespie et al (2024) Neurofeedback training can modulate task-relevant memory replay rate in rats | 16.8 TB, 114 assets | Rat, 4 | CA1 tetrodes, behaviour/position; spike units not listed in variableMeasured | Control cohort is in 000115 per description. |
| DANDI:000061 | Reactivations of emotional memory in the hippocampus-amygdala system during sleep | 1.95 TB, 40 assets | Brown rat, 4 | Units + LFP; sleep before/after training on linear track per description; no Position variable listed | Hippocampus-BLA reactivation. |
| DANDI:000059 | Cooling of Medial Septum Reveals Theta Phase Lag Coordination of Hippocampal Cell Assemblies | 2.9 TB, 100 assets | Norway rat, 5 | Units, Position, LFP; sleep not stated | Large. |
| DANDI:001775 | Mouse hippocampal electrophysiology during spatial working memory and consummatory behavior | 66.2 GB, 85 assets | Mus musculus, 6 | Sorted spikes (MountainSort4), LFP, position: yes; sleep not stated | Mouse, smaller. |
| DANDI:001695 | High-density extracellular recordings (Neuropixels/SiNAPS) of hippocampal-cortical dynamics | 3.1 GB, 22 assets | Mus musculus, 6 | Units, Position; description: homecage rest, spatial navigation, sensory stimulation; hippocampus + retrosplenial cortex | Smallest ephys set found; also relevant to cortex-hippocampus reactivation. |
| DANDI:000718 | Offline ensemble co-reactivation links memories across days | 40.6 GB, 20 assets | Mus musculus, 2 | One-photon calcium imaging (not spikes); offline reactivation is the topic | Calcium-imaging reactivation data. |
| DANDI:000218 | Routing of Hippocampal Ripples to Subcortical Structures via the Lateral Septum | 1.5 TB, 98 assets | Norway rat, 7 | Units, LFP, Position | SWR-LS coupling; replay content not the focus per description. |

Not selected: 001634 (6.4 TB, 16,699 assets, theta-disruption study, Units+Position) listed but very large. "DANDI search" returned 68 hits for "hippocampus", 8 for "replay", 8 for "sleep hippocampus"; I reviewed only the metadata of those shown.

### 6b. Zenodo (CC0 / CC-BY, `access_right: open`)

| Zenodo ID | Title | Size | Licence | DOI | Note |
|---|---|---|---|---|---|
| 5566548 | LFP and single-unit data published in Olafsdottir, Carpenter and Barry (2016) Nature Neuroscience 19: 792-794 | 9.9 GB (1 file) | CC-BY-4.0 | 10.5281/zenodo.5566548 | Axona tetrodes, 8 MEC + 8 hippocampus; filenames indicate running on a Z-track, sleepPOST, foraging (description). Spike/LFP + sleep. https://zenodo.org/records/5566548 |
| 7114733 | Experience-driven rate modulation is reinstated during hippocampal replay | 14.6 GB, 31 files | CC0 | 10.5061/dryad.ksn02v76h | Description: dorsal CA1 place cells; replay defined by rate as well as place; directly on the rate/sequence question. https://zenodo.org/records/7114733 |
| 5587779 | Data from: Hippocampal replay of experience at real-world speeds | 72.3 GB, 10 files | CC0 | 10.7272/Q61N7ZC3 | Data of the Denovellis 2021 paper in the capsule. https://zenodo.org/records/5587779 |
| 5594801 | Hippocampal ensembles represent sequential relationships among an extended sequence of nonspatial events | 194 MB, 1 file | CC0 | 10.7280/D14X30 | Rat hippocampal ensemble data, non-spatial sequence; small. |
| 4603831 | Synchronous activity patterns in the dentate gyrus during immobility | 114 MB, 1 file | CC0 | 10.5061/dryad.mkkwh70z6 | Dentate gyrus structured activity during immobility/sleep (description); modality not checked. |

Count: 10 DANDI + 5 Zenodo. figshare and OSF were not searched.

---------------------------------------------------------------------------------

## 7. LLM / agent systems for neuroscience data and electrophysiology

| # | Title | Authors | Year | Venue | ID | Note (abstract) |
|---|---|---|---|---|---|---|
| 7.1 | SpikeLab: Agentic tools for spike data analysis | Van der Molen T, Cheney L, ..., Sharf T | 2026 | bioRxiv preprint (PMC13142478) | doi:10.64898/2026.04.25.720833 | Text-to-analysis framework for neural spike data; composable data structures + skill-based agentic system enforcing "bounded autonomy": mandatory expert-vetted methods, correctness over efficiency, clarification-seeking. Closest match to the project. Code link not looked up. |
| 7.2 | Facilitating analysis of open neurophysiology data on the DANDI Archive using large language model tools | Magland JF, Ly R, Rubel O, Dichter B | 2025 | Sci Data | doi:10.1038/s41597-025-06285-x, PMC12727687 (OA); preprint 10.1101/2025.07.17.663965 | LLM + agentic tools guide users through access, visualisation, preliminary analysis of DANDI data; notebook generator analyses dataset structure and executes inspection scripts. |
| 7.3 | Spike sorting AI agent (SpikeAgent) | Lin Z, Marin-Llobet A, ... | 2025 | bioRxiv preprint (PMC11844495) | doi:10.1101/2025.02.11.637754 | Multimodal LLM-based agent that automates the spike sorting pipeline and offers automated interpretability of spiking data. |
| 7.4 | NS-Copilot: An LLM-Driven Agent System for Autonomous Neuroscience Analysis | Liu W, Qiao Y, ... | 2026 | arXiv | arXiv:2609.01971 | Multi-agent system over domain-specific pretrained models; supports EEG and extracellular spike data via natural language. |
| 7.5 | SeekBrain: An Autonomous Multi-Agent System for Accelerating Neuroscience Discovery | Wu J, Xiang P, ... | 2026 | arXiv | arXiv:2607.29347 | Autonomous multi-agent framework with domain-grounded hierarchical planning for heterogeneous neuroscience data (abstract cut off). |
| 7.6 | A case study of evaluating AI agents on a neuroscience data-to-discovery pipeline | Horstmann KA, Lin E, ... | 2026 | arXiv | arXiv:2606.07718 | Empirical study of general-purpose coding agents on a fly optogenetics data-to-discovery pipeline; stresses correctness and robustness matter more than implementation detail. Useful design/evaluation analogue for the loop. |
| 7.7 | An AI Agent for cell-type specific brain computer interfaces | Marin-Llobet A et al | 2025 | bioRxiv preprint (PMC12458948) | doi:10.1101/2025.09.11.675660 | Appeared in the same search; I saw only the title. Weak relevance. |

Also seen, EEG-specific (not ephys spikes): EEGAgent arXiv:2511.09947, EEGAgentBench arXiv:2609.31632, Agentic EEG Pipeline Synthesis (Sensors, doi:10.3390/s26206472), BrainAgent arXiv:2606.25400. Titles only.

Count: 7 (6 relevant to spikes/ephys).

---------------------------------------------------------------------------------

## Not found / could not verify (left out)

- No paper found that specifically quantifies false-positive rates of different replay shuffles apart from Trimper 2017 and Takigawa 2024 (both in earlier capsule). Europe PMC queries for replay AND shuffle AND false positive returned zero hits.
- No replay paper found that directly compares firing-rate-matched / rate-preserving shuffles with cell-ID or place-field shuffles. The nearest items are the generic surrogate papers in topic 1, plus 1b.3 and 1b.5 (rate alone can generate sequence-like effects).
- No systematic time-bin-size study of replay detection (beyond Chen 2016 and Box 2016 in the earlier capsule). Topic 2 additions are mostly general-purpose neural-population papers; only 2.1, 2.5, 2.6 are about reactivation/assemblies.
- Lognormal firing-rate distribution: only the Mizuseki and Miyawaki snippet (1b.4, "skewed networks") touches it. I did not search for the lognormal literature separately.
- No Python package found for PCA/ICA assembly detection with a clear licence; the only Python route verified is Elephant `cell_assembly_detection` (CAD). The PCA/ICA repo (tortlab) is MATLAB with no licence detected.
- SpiSeMe: paper found, code repo and licence not found. FIM / SPADE paper link to Elephant `spade.py` not verified beyond a filename.
- Licence of the two DurstewitzLab/tortlab repos: GitHub API reported none; a LICENSE file might exist in a non-standard form. Not checked.
- GitHub data comes from unauthenticated API (rate-limited); "pushed" date is not necessarily the last default-branch commit.
- conda availability: confirmed only for spikeinterface, pynwb, dandi (conda-forge). For elephant, pynapple, neo, neuroconv, ripple-detection, nelpy, non-local-detector the anaconda.org lookup under the same name returned "could not be found"; they may exist under another channel or name. pip is the verified route.
- DANDI 000115 / 000629 / 000059 / 000218 / 001775: whether each has an NWB Units table (sorted spikes) was not confirmed for all; `variableMeasured` omitted Units for 000115 and 000629. Sleep epochs were stated in the description only for 000044, 000978, 000061, 001695, and in the Zenodo 5566548 filenames.
- figshare, OSF, Dryad (direct), CRCNS: not searched / not reachable without login in this session. Zenodo hits 7114733, 5587779, 5594801, 4603831 carry Dryad DOIs; I did not open Dryad.
- Full texts: none read. Abstracts were sometimes truncated by the search index; claims are limited to what was visible.
- Search outputs for arXiv-only items (NS-Copilot, SeekBrain, Horstmann) come from the Firecrawl index; arXiv pages themselves were not opened.
