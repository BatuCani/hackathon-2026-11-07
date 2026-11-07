# Research capsule: hippocampal replay / reactivation

Merged from two independent literature passes (Claude and Codex) on 2026-11-07, for the Claude Impact Lab x Foresight hackathon at CIC Berlin.

## How to use this folder
- This README is the index. [ADDENDUM.md](ADDENDUM.md) holds the second research pass: surrogate/shuffle controls, bin-size effects, preplay critiques, cortical reactivation, Python packages, no-registration datasets and agent systems for spike data. [BUILD_APPROACH.md](BUILD_APPROACH.md) is a time-boxed build plan.
- Third-party papers and code are **not stored here**. Run `bash research/scripts/fetch_sources.sh` to pull open-access full text (Europe PMC API) and clone the reference repos into `research/_fetched/` (git-ignored).
- The one PDF kept in `papers/` is Takigawa et al. 2024, which is CC BY.

## Evidence rules
- Every item was returned by a live lookup (Europe PMC / bioRxiv / arXiv metadata, the GitHub API, or the publisher page). Nothing comes from memory alone.
- "Read" means someone opened the text. Most items were identified from abstracts and metadata only; check the paper before you cite a specific claim.
- Europe PMC PDF links sit behind a bot check. That was not bypassed; full text comes from the REST API instead.
- The project repo started as a single README, so there is no existing code to build on.

## Anchor paper
Tingley D, Peyrache A (2020). *On the methods for reactivation and replay analysis.* Phil Trans R Soc B 375:20190231. doi:10.1098/rstb.2019.0231, PMC7209909.
Read from the PDF:
- Reactivation (zero-lag) and replay (temporal structure) methods are applied inconsistently; no two studies use the same approach.
- Open gaps it names: firing-rate bias in cell-pair correlation, lognormal firing-rate distributions, an unexplored effect of time-bin size, and no systematic comparison of methods.
- It calls for direct comparison of methods, a community code base and a taxonomy.
- Its code is `DavidTingley/RnR_methods` (MATLAB).

## Recommended build claim (Codex capsule, adopted)
Build a **reproducible replay-candidate analyser**, not a system that claims to prove replay.
Pipeline: input validation, movement-only place fields, candidate population bursts, Bayesian decoding, trajectory score, several shuffle nulls, auditable report.
Honest demo: on a linear-track dataset (real or simulated), recover injected sequences while measuring the false-positive rate on shuffled data.
Steps and tests: see [BUILD_APPROACH.md](BUILD_APPROACH.md).

Design points the sources support:
1. Separate candidate selection (bursts, optional ripple power) from sequence validation.
2. Learn place fields from running data only, then freeze them when decoding rest.
3. Start with a transparent Poisson naive-Bayes decoder and save the whole posterior.
4. Use at least two shuffle nulls; Takigawa et al. report that conclusions depend on the null chosen.
5. Report the empirical false-positive rate, not only the nominal p-value.

What not to overclaim:
- A low shuffle p-value is evidence against that null, not proof of a remembered trajectory.
- Thresholds (bin width, smoothing, speed cutoff, burst, ripple) depend on data and experiment; log them.
- Do not compare algorithms by raw detection counts alone.

## Update after the second pass (details and per-item verification in ADDENDUM.md)
- **Data without registration:** DANDI:000044 (Grosmark & Buzsaki; CC-BY-4.0, NWB, 4 rats, PRE sleep / novel maze / POST sleep). Its description matches CRCNS hc-11. It is 73 GB, so stream only the Units table. Title, size and licence were re-checked against the DANDI API. Other sets (000978, 001695, Zenodo 7114733 and 5587779) are in ADDENDUM section 6.
- **Python null-model toolbox:** `pynapple` 0.11.4 (MIT; `jitter_timestamps`, `shuffle_ts_intervals`, `decode_bayes`) and `Elephant` 1.2.1 (BSD-3; `spike_train_surrogates`, `cell_assembly_detection`). Versions and licences re-checked on PyPI. `nelpy`, `non-local-detector` and `replay-trajectory-classification` lag on PyPI; install from GitHub.
- **Shuffle theory:** van der Meer, Kemere & Diba 2020 (doi:10.1098/rstb.2019.0238) says the central problem is constructing and interpreting chance distributions. Platkiewicz 2017 and Louis 2010 show spike-centred jitter can inflate false positives and that dithering in operational time conserves rate and ISI.
- **Closest prior art for the project:** SpikeLab (bioRxiv 2026, doi:10.64898/2026.04.25.720833) and Magland et al. 2025 (Sci Data, doi:10.1038/s41597-025-06285-x). Read them before pitching novelty.
- **Open gap the searches did not close:** no paper found that compares rate-matched replay shuffles with cell-ID or place-field shuffles, and no systematic bin-size study of replay. A loop that sweeps shuffle type and bin size on one dataset would address both; this is a suggestion, not a finding.

## Code (clone with the fetch script)
| Repo | Use | Language / licence |
|---|---|---|
| [bendor-lab/replay_detection_cross_validation](https://github.com/bendor-lab/replay_detection_cross_validation) | Companion code to Takigawa 2024: Bayesian decoding and track log-odds on simulated replay | MATLAB, CC0-1.0 |
| [DavidTingley/RnR_methods](https://github.com/DavidTingley/RnR_methods) | Anchor paper toolbox: `ReactStrength` (PCA/ICA), `replay_Bayesian`, `replay_RankOrder`, `compareReplayMethods`, `compareNoiseDegradation`. No Python version, so a port is a clear gap. | MATLAB, GPL-3.0 (GitHub API) |
| [Eden-Kramer-Lab/replay_trajectory_classification](https://github.com/Eden-Kramer-Lab/replay_trajectory_classification) | State-space decoding, sorted or clusterless spikes. Stretch goal after a baseline. | Python, MIT |
| [LorenFrankLab/non_local_detector](https://github.com/LorenFrankLab/non_local_detector) | Newer HMM / Bayesian package for non-local activity (last commit 2026-11-06) | Python, MIT |
| [kemerelab/UncoveringTemporalStructureHippocampus](https://github.com/kemerelab/UncoveringTemporalStructureHippocampus) | Notebooks for Maboudi 2018 (HMM vs Bayesian replay) | Python notebooks, MIT |
| [nelpy/nelpy](https://github.com/nelpy/nelpy) | Electrophysiology object model; used by the Maboudi analysis per the Codex capsule | Python, MIT |
| [FeeLab/seqNMF](https://github.com/FeeLab/seqNMF) | seqNMF code from Mackevicius 2019, with demo data | MATLAB, LICENSE file present |

Licences marked MIT / CC0 were checked in the cloned LICENSE files on 2026-11-07.
Hackathon repo of record: https://github.com/xemantic/claude-impact-lab-2026 (HTTP 200; not cloned).

## Papers
Replay and reactivation methods, validation, critiques
1. Takigawa, Huelin Gorriz, Tirole, Bendor (2024). *Evaluating hippocampal replay without a ground truth.* eLife. doi:10.7554/eLife.85635. **Best validation guide.** Compares rank-order, weighted-correlation and linear-fit scoring and proposes a two-track log-odds check. CC BY. PDF in `papers/`.
2. Trimper, Trettel, Hwaun, Colgin (2017). *Methodological caveats in the detection of coordinated replay between place cells and grid cells.* Front Syst Neurosci. doi:10.3389/fnsys.2017.00057. Some analyses detect replay spuriously; stricter controls reduce false findings.
3. Kern et al. (2025). *Challenges in replay detection by TDLM in post-encoding resting state.* eLife. doi:10.7554/eLife.108023.
4. Maboudi et al. (2018). *Uncovering temporal structure in hippocampal output patterns.* eLife. doi:10.7554/eLife.34467. HMM method; replay identified without the place code.
5. Denovellis et al. (2021). *Hippocampal replay of experience at real-world speeds.* eLife. doi:10.7554/eLife.64505.
6. Box, Jones, Whiteley (2016). *A hidden Markov model for decoding and the analysis of replay in spike trains.* J Comput Neurosci. doi:10.1007/s10827-016-0621-9 (arXiv:1412.6469).
7. Chen, Grosmark, Penagos, Wilson (2016). *Uncovering representations of sleep-associated hippocampal ensemble spike activity.* Sci Rep. doi:10.1038/srep32193. Bin size, firing rate and neuron count affect reliability.
8. Liu, Grosmark, Chen (2018). *Methods for assessment of memory reactivation.* Neural Comput. doi:10.1162/neco_a_01090. Proposes a weighted distance correlation.
9. Huh, Yun, Lee, Jung (2026). *A likelihood-based method for identifying replay from spike sequences.* Nat Commun. doi:10.1038/s41467-026-74822-2.
10. Wu, Wei (2026). *Drift-diffusion dynamics of hippocampal replay.* PLoS Comput Biol. doi:10.1371/journal.pcbi.1014761.
11. Zeng, Eden (2025). *A state-space framework for causal detection of hippocampal ripple-replay events.* IEEE TBME. doi:10.1109/TBME.2025.3578583 (arXiv:2502.05394).
12. Ólafsdóttir, Bush, Barry (2018). *The role of hippocampal replay in memory and planning.* Curr Biol. doi:10.1016/j.cub.2017.10.073. Review that covers replay analysis methods.
13. Davidson, Kloosterman, Wilson (2009). *Hippocampal replay of extended experience.* Neuron. doi:10.1016/j.neuron.2009.07.027. Radon-integral score (cited in RnR_methods).
14. Gupta et al. (2010). *Hippocampal replay is not a simple function of experience.* Neuron. doi:10.1016/j.neuron.2010.01.034.
15. Wilson, McNaughton (1994). *Reactivation of hippocampal ensemble memories during sleep.* Science. doi:10.1126/science.8036517.
16. Chen, Wilson (2023). *How our understanding of memory replay evolves.* J Neurophysiol. doi:10.1152/jn.00454.2022.
17. Zhang, Ou, Liu (2025). *Replay and ripples in humans.* Annu Rev Neurosci. doi:10.1146/annurev-neuro-112723-024516.
18. Zheng et al. (2025, bioRxiv preprint). *From labels to latents: ... Jump Latent Variable Model.* doi:10.1101/2025.12.14.694183.

Assembly and sequence detection
19. Mackevicius et al. (2019). *Unsupervised discovery of temporal sequences in high-dimensional datasets (seqNMF).* eLife. doi:10.7554/eLife.38471.
20. Williams, Degleris, Wang, Linderman (2020). *Point process models for sequence detection in high-dimensional neural spike trains.* arXiv:2010.04875.
21. Lopes-dos-Santos et al. (2011). *Neuronal assembly detection and cell membership specification by PCA.* PLoS ONE. doi:10.1371/journal.pone.0020996.
22. Peyrache et al. (2010). *PCA of ensemble recordings reveals cell assemblies at high temporal resolution.* J Comput Neurosci. doi:10.1007/s10827-009-0154-6.
23. Watanabe et al. (2019). *Unsupervised detection of cell-assembly sequences by similarity-based clustering.* Front Neuroinform. doi:10.3389/fninf.2019.00039.
24. van de Ven et al. (2016). *Hippocampal offline reactivation consolidates recently formed cell assembly patterns during sharp wave-ripples.* Neuron. doi:10.1016/j.neuron.2016.10.020.
25. Giri et al. (2019). *Hippocampal reactivation extends for several hours following novel experience.* J Neurosci. doi:10.1523/JNEUROSCI.1950-18.2018.
26. Kudrimoti, Barnes, McNaughton (1999), PMID 10234037; Nádasdy et al. (1999), PMID 10531452. Classic reactivation and sequence-replay papers.

AI research loops (the hackathon format). Titles and IDs checked against the arXiv PDFs; results not reviewed.
27. *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery.* arXiv:2408.06292.
28. *The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search.* arXiv:2504.08066.
29. Mitchener et al. (2025). *Kosmos: An AI Scientist for Autonomous Discovery.* arXiv:2511.02824.
30. Ifargan, Hafner, Kern, Alcalay, Kishony (2024). *Autonomous LLM-driven research from data to human-verifiable research papers.* arXiv:2404.17605.

## Open data (not downloaded; check licence and format first)
- DANDI:000044 is the no-registration route to the same Grosmark & Buzsaki recordings (see update above). CRCNS hc-11 (Buzsaki lab): eight bilateral silicon-probe recordings from four Long-Evans rats. https://crcns.org/data-sets/hc/hc-11/about-hc-11 (free account needed).
- CRCNS hippocampus index: https://crcns.org/data-sets/hc
- Neurosharing paper describing the CRCNS spike/LFP sets: PMC4097350.
- DANDI post on place-cell recordings from the Space Shuttle: https://about.dandiarchive.org/blog/2026/02/27/place-cells-in-space-hippocampal-recordings-from-the-space-shuttle/
- Takigawa 2024 and Maboudi 2018 each have a companion code repo (see Code table).
- No dataset has been tested with the code here.

## Gaps
- Shuffle-comparison and bin-size studies for replay were searched for and not found (see ADDENDUM). figshare, OSF and CRCNS were not searched.
- The AI-loop papers were not read in depth.
- `fetch_sources.sh` was syntax-checked only; Europe PMC returns no full text for non-open-access papers, and the script skips those.
