# Briefing: Tingley & Peyrache (2020) x research loop x Claude Impact Lab Berlin

As of 2026-11-07, 13:30 CET.
Familiarization briefing for the team: the anchor paper, what the lab expects, and candidate questions for the afternoon.
Translated from the German original.
Quotes from the paper are verbatim, with section references in parentheses.

## TL;DR

- The paper is a methods review: it shows that reactivation and replay results depend strongly on the method, not only on the data.
- Key numbers to recompute: event-by-event agreement between rank-order and weighted correlation is only R = 0.126, weighted correlation vs. Radon R = 0.43, rank-order vs. Radon R = 0.07 (n.s.); 5-20 % of all candidate events are typically called "significant"; random sequences of length 10 are "significant" in 5-12 % of cases, and up to 20 % at length 5.
- The paper itself names open gaps ("still missing", "lacking"): the firing-rate confound in pairwise correlations and a systematic variation of bin size.
  These are ideal, computationally checkable hackathon questions.
- The lab repo (xemantic/claude-impact-lab-2026) has no problem catalogue; the scientists bring their problems in the pitch.
  So the paper is not a predefined lab problem but our team's topic (dropdown field "Neuroscience").
- Best afternoon candidates (by feasibility): A) rank-order false-positive rate, B) PCA vs. ICA + Marchenko-Pastur, C) firing-rate confound in EV/REV, D) bin size, E) replication of the method agreement on public Grosmark data (DANDI 000044).
- License trap: the reference toolbox RnR_methods is GPL; the lab default is Apache 2.0. Better to reimplement in Python from the paper than to copy code.
- Timing: per the lab agenda, lunch is 13:00-14:00 and submission is 17:00, demos from 17:15 at 3 minutes each (the diagram says 4 minutes).

## 1. Sources

- Full text of the paper from the publisher page (royalsocietypublishing.org, DOI 10.1098/rstb.2019.0231), including references and the first page of the Supplementary Information.
- The lab repo, read in full: README.md, RESEARCH-LOOPS.md, CLAUDE.md, `.claude/skills/judge-submissions/SKILL.md`, `.github/ISSUE_TEMPLATE/project-submission.yml`, config.yml, the LICENSE files.
  The repo has 0 issues, 0 PRs, no datasets and no starter code.
- The event slides linked from the lab README.
- The reference toolbox `github.com/DavidTingley/RnR_methods` (MATLAB, GPL-3.0, last push 2021-05).
- Datasets checked through the DANDI API and a request to the old Buzsáki lab URL.
- A small control calculation of the rank-order false-positive rate, to anchor the answer key for candidate A (see section 5).

## 2. The paper in 2 minutes

Tingley D., Peyrache A. (2020) "On the methods for reactivation and replay analysis", Phil. Trans. R. Soc. B 375: 20190231, DOI 10.1098/rstb.2019.0231.
Review article, free to read, part of the Theo Murphy issue "Memory reactivation".
Citation, links and license status: [papers/README.md](papers/README.md).

### Reactivation vs. replay

> "These methods primarily fall into two categories, those that quantify zero-lag relationships without examining temporal evolution, termed reactivation, and those that quantify the temporal structure of changing activity patterns, termed replay." (Abstract)

- Reactivation: zero-lag co-activity of neurons during sleep resembles that during waking.
  Bins typically 50-200 ms.
- Replay: the temporal order (sequence) from behaviour reappears during sleep or rest, usually compressed in time.
  Bins typically 10-50 ms.
- Standard paradigm: PRE sleep (control) -> new environment/maze (template) -> POST sleep.
  > "using the pre-behaviour epoch as an internal control to determine if such activity patterns were pre-existing." (1 Introduction)
- The paper's guiding statement:
  > "the observation and quantification of such patterns depend intimately on the choice of methods used for detection and statistical assessment of their existence." (1 Introduction)

### Method families

| Family | What is measured | Assumptions | Criticism in the paper |
|---|---|---|---|
| Cell-pair correlation, explained variance (EV) / reverse EV (REV) | Partial correlation of pair correlations wake-POST, controlling for wake-PRE: EV = ((r_W,POST - r_W,PRE * r_PRE,POST) / sqrt((1 - r_W,PRE^2)(1 - r_PRE,POST^2)))^2. REV: PRE and POST swapped; reactivation = EV > REV across sessions | Change in correlation = learning; temporally "forward" | No noise control; ignores firing-rate changes; no temporal resolution; finite data always produce non-zero correlations (2a) |
| Reactivation strength (projection) | R(t) = z(t)^T P_wake z(t), P = correlation matrix with zero diagonal | z-scoring normalizes rates | Strongly driven by high-firing neurons; noisy correlations mask the signal (2b) |
| PCA + Marchenko-Pastur | Significant components = eigenvalues above the random bound; R(t) per component with projector P = v v^T | Components orthogonal; random bound from random matrix theory or bin shuffle | The orthogonality constraint handles overlapping assemblies poorly (2c, 2d) |
| ICA (Lopes-dos-Santos et al. 2013) | De-mixing of the significant PCs into independent components | As PCA, plus independence | Separates overlapping assemblies, "a situation in which PCA fails" (2e); less explained variance, but more interpretable |
| Cross-correlogram asymmetry (Skaggs & McNaughton 1996) | B_ij = integral CCG(0..200 ms) - integral CCG(-200..0 ms); correlation of B_behav with B_post vs. B_pre | Pairwise temporal order is enough | Sensitive to preprocessing, event inclusion, rate distributions (3a) |
| Template correlation with scaling factor (Louie & Wilson 2001, Lee & Wilson 2002) | Correlation of template vs. sleep activity, template compressed 0.5-20-fold | Linear time mapping behaviour -> replay | Linearity breaks with variable replay speed (3b-i) |
| Rank-order correlation (Foster & Wilson 2006, Diba & Buzsáki 2007) | Correlation of firing order within the event with place-field order | Only order matters; cells with one field | Cells with multiple fields usually excluded; high false-positive rates with few cells (3b-ii, 3b-iv) |
| Weighted distance correlation (Liu, Grosmark, Chen 2018) | Ordinal relationship, robust to "gaps" | No linearity required | More robust than rank-order and weighted correlation when there are gaps (3b-ii) |
| Bayesian decoding + line fitting (Zhang 1998; Radon: Davidson 2009; weighted correlation: Wu & Foster 2014) | Posterior P(x given n) per 10-50 ms bin over a 50-500 ms event; goodness measure: Radon integral/slope or linear weighted correlation | Poisson spikes, independent neurons, continuous trajectory | Bin size changes the result; variable bins (fixed spike count) give similar results (3b-iii) |
| Template-free methods (unsupervised: time-series decomposition, clustering, state models, deep learning) | Patterns without a behavioural template | - | Patterns are hard to "ground" in behaviour (4b) |

### Null models and shuffles the paper discusses

- Bin-to-bin shuffle per cell as the null for eigenvalues, equivalent to the analytical Marchenko-Pastur bound (2d).
  > "any PC whose eigenvalue exceeds the theoretical upper bound can be considered significant with almost absolute certainty" (2d)
  Formula (standard RMT, not verbatim in the text): lambda_max = (1 + sqrt(N/B))^2 for N neurons and B bins.
- REV as the control for EV (2a).
- Rate matching by subsampling spikes or by very large bins, to separate rate effects from correlation effects (2a).
- Within-event shuffles for replay, the main criticism:
  > "All current approaches have used a within-event shuffling approach. [...] consistently 5–20% of all candidate events are typically detected as significant replay events" (3b-iv)
  > "a random sequence generator (length = 10) can provide significant rank-order correlations with any random template sequence approximately 5–12% of the time (n = 100 events), and when shorter sequences are examined (length = 5) the false positive rate can reach up to 20%" (3b-iv)
  > "examining the proportion of significant events, out of all candidate events, is necessary" (3b-iv)
- Real spike orders are more constrained than random ones, and fast neurons fire first after silence; a pure random permutation is therefore only a lower bound on false positives (3b-iv).
- Stella et al. 2019: replay trajectories as a whole fit Brownian diffusion, not necessarily experienced paths (3b-iv).

### The central empirical claim (Fig. 3, 4)

- One dataset (n = 39 recordings, 5 rats; Tingley & Buzsáki 2018), 54 templates (linear tracks), at least 6 place cells with exactly one field, uniform event detection.
- Event-by-event correlation of replay scores: rank-order vs. weighted correlation R = 0.126; weighted correlation vs. Radon R = 0.43; rank-order vs. Radon R = 0.07, not significant (3b-iv).
  > "the determination of which candidate replay events are significant ‘replays’ may depend on the method used, rather than the underlying neural activity pattern." (3b-iv)
- "Similar results were observed using simulated data and an alternative previously published dataset [30]" - [30] is Grosmark & Buzsáki 2016, public as DANDI 000044.
  This replication is not shown in the paper.
- Fig. 4: simulation with 100 cells, 1 spike each per event, plus inserted noise spikes and removed true spikes; each method degrades differently.

### Explicitly open gaps (good research questions)

- Firing-rate confound:
  > "the change in intrinsic excitability initially reported in the hippocampus [17] could explain, at least in part, the change in cell-pair correlation [68]. A systematic review and analysis of this possibility is still missing in the field." (3b-v)
- Bin size:
  > "a systemic variation of bin size and its impact on pattern detection is lacking. Preliminary simulations suggest bin size can greatly alter how some template-based replay detection methods perform" (3b-v)
- Lognormal rates (about 0.001-100 Hz): methods are dominated by a few fast neurons (3b-v).
- Circadian and metabolic effects over 3-10 h experiments not examined (3b-v).
- Templates for non-spatial content unclear (3b-iv).

### Recommendations

- > "These observations should instead be validated by multiple and, if possible, previously established tests." (Abstract)
- > "it will be crucial for researchers to directly compare multiple methods" (4a); a shared community code base or a methods taxonomy.
- Assess the proportion of significant events against an across-event null instead of only testing single events against within-event shuffles (3b-iv).
- Perspective of the downstream neuron: Hebbian learning with normalization approximates PCA (Oja 1982) (5).

## 3. What the lab expects (xemantic/claude-impact-lab-2026)

### Repo contents

- README.md: event "Claude Impact Lab x Foresight Institute", link to the presentation, licenses: code Apache 2.0, text CC BY 4.0, everything donated to the Foresight Institute; another open-source license only if everyone agrees; GPL/AGPL dependencies can determine the license.
- RESEARCH-LOOPS.md: `/goal <checkable condition>`, `/loop <interval> <prompt>`, Claude Science, loop prompt template with TASKS.md, PROMPT.md, JOURNAL.md, a subagent per atomic step, a commit per task, test-first ("a test can check a known result: an analytic solution, a published value, a conservation law").
- CLAUDE.md: semantic line breaks in Markdown; in auto mode never commit on its own.
- `.github/ISSUE_TEMPLATE/project-submission.yml` (the "/submit issue"): title `[Submission] <team name>: <one-line project title>`, label `submission`, required fields: team, members with role, field (including Neuroscience), public repo, license, open problem (including "How can its results be checked computationally?"), the research loop (link the files), what the loop found (links + verification + confidence), where it got stuck, what it would need next, how to run it; optional: data and sources, how Claude was used, demo materials; three required checkboxes (public + license, no secrets, CC BY 4.0 for the text).
- `.claude/skills/judge-submissions/SKILL.md`: Claude assesses each submission, checks every claim against repo files (supported/partly/unsupported/contradicted), runs no code, checks the license, scores 1-5 for problem, loop, evidence, honesty, reproducibility.
  > "Do not reward length or polish. An honest, well-verified negative result beats an impressive claim the repository does not support."
- No problem list, no data, no starter code, no scientist descriptions in the repo.

### Agenda per the slides

- 10:00 talks, 10:30 scientist pitches (max. 3 min: question, available data, what a useful result would be), 11:00 team formation, 11:30 build 1, 13:00 lunch, 14:00 build 2, 17:00 submission deadline, 17:15 demos (3 min, start with the team name), 18:15 jury (Keith Patarroyo decides with Claude reviews), 18:30 winners.

### Mapping lab -> research-loop diagram

See [research-loop.png](research-loop.png).

| Diagram | Lab requirement | Comment |
|---|---|---|
| SCIENTIST: question, answer key, final say | "The scientist stays with the team all day as the expert on the question" | Matches |
| 1 QUESTION (PROBLEM.md) | Issue field "Open problem" including computational checkability; jury criterion "Problem: open, significant, and checkable by computation" | PROBLEM.md becomes the direct source for this field |
| 2 ANSWER KEY (number + unit + threshold) | `/goal` needs "a number within a tolerance" | The answer key is also the `/goal` condition |
| 3 REFEREE (locked) | Test-first; "a test can check a known result" | Referee = test against an analytical solution or a published value |
| 4-8 READ/PREDICT/RUN/JUDGE/RECORD | Criterion "Loop: reads literature, writes and runs code, checks its own results, keeps its state in files"; TASKS.md, JOURNAL.md, PROMPT.md | Notebook = JOURNAL.md; labels verified/contradicted/not enough evidence match the judge's supported/contradicted/unsupported |
| 9 VETO | Scientist as problem owner | Not formally in the repo, but in the slide format |
| 10 FINDINGS (only numbers with a file) | Criterion "Evidence" and field "What the loop found" with links; the judge checks every claim against files | Exactly what the judge skill penalizes when it is missing |
| Notebook: failures too | Criterion "Honesty", field "Where it got stuck" | Negative results explicitly count |
| 11 REPRO + SUBMIT (one command) | Criterion "Reproducibility", field "How to run it" | One command, public data, no keys |
| SHIP by 17:00, 4-min demo | Submission 17:00, demo 3 min from 17:15 | Cut the demo to 3 min |
| LOOP 13:00-16:00 | Lunch 13:00-14:00 | Effectively about 2 h of active loop time, unless the loop runs autonomously over lunch |

### How the paper relates to the lab

- The paper is not a predefined lab problem; the lab does not set problems.
- It fits the format: Neuroscience is a field in the template, the paper supplies published numbers as referee anchors, and it names open, computationally checkable gaps itself.
- License: RnR_methods is GPL (repo license GPL-3.0, file headers "GPL v2 or later").
  Copying or porting code from it forces the team repo to GPL, and the judge checks that.
  Recommendation: reimplement from the paper's formulas (Python), only cite the toolbox.
- Data: DANDI 000044 is CC-BY-4.0, compatible with the lab license.

## 4. Datasets and compute load

| Source | Contents | Size | Suitability |
|---|---|---|---|
| Synthetic (Poisson neurons, planted assemblies/sequences) | Ground truth known | MB, seconds to minutes of CPU | Best basis for referees; the paper's own Fig. 4 simulations are synthetic too |
| DANDI 000044, Grosmark & Buzsáki 2016 (ref. [30]) | 8 sessions, 4 rats, PRE (~4 h) / MAZE (~45 min, linear or circular) / POST (~4 h); NWB with units, position, LFP; CC-BY-4.0 | 5.4-10.4 GB per NWB, mostly LFP | Feasible by streaming only units/position (pynwb + remfile/fsspec), not loading everything; smallest session: `sub-Buddy_ses-Buddy-06272013` (5.4 GB, 1.6 m linear platform) |
| DANDI 000213, Tingley & Buzsáki 2018 (ref. [61], main dataset of Fig. 3) | Hippocampus-lateral septum | about 1.5 TB | Too large for the afternoon |
| Old Buzsáki lab URL from `RnR_methods/data/.../download_DATA.m` | The paper's example session | - | Dead: HTTP 301 to `buzsakilab.com/wp/datasets/` |
| DANDI 000115 / 000629 (Gillespie et al., Frank lab) | Replay datasets | 9-17 TB | Too large |

Compute: Python with numpy and scipy is enough for candidates A-D.
All candidates A-D run in seconds to a few minutes on one core; E needs network streaming (a few 100 MB) and a few GB of RAM.

## 5. Candidate questions for the afternoon (by feasibility)

The choice belongs to the scientist and the team; these are options.
All answer keys are proposals to sign off, not fixed.

### A. What is the true false-positive rate of the rank-order method? (feasibility: very high)

- Question: Does the paper's claim hold (length 10: 5-12 %, length 5: up to 20 %), and where does it come from: real inflation above 5 %, or only discreteness plus spread across sessions?
- Control calculation (Pearson on ranks with t approximation, two-sided p < 0.05, random permutation against the template; exactly enumerated for L <= 8, 200 000 Monte Carlo draws for L = 9, 10):

  | Length L | exact FP rate | 95 % range per session (100 events) | median of the maximum over 100 sessions |
  |---|---|---|---|
  | 3 | 33.33 % | 24-43 % | 45 % |
  | 4 | 8.33 % | 3-14 % | 16 % |
  | 5 | 8.33 % (= 10/120) | 3-14 % | 16 % |
  | 6 | 5.83 % | 2-11 % | 12 % |
  | 7 | 4.80 % | 1-9 % | 11 % |
  | 8 | 5.76 % | 2-11 % | 12 % |
  | 10 | 5.50 % | 2-10 % | 12 % |

  Reading: "5-12 %" at L = 10 is mean to worst case across sessions; "up to 20 %" at L = 5 is the worst-case tail of an exact 8.33 % rate.
- Answer key (proposal): exact FP rate at L = 5 = 8.33 % (tolerance ±0.01 percentage points, analytically 10/120); at L = 10 = 5.5 % (±0.3 pp); the paper's claim counts as "verified" if the worst case over 100 sessions of 100 events each lies within 10-14 % at L = 10 and within 14-22 % at L = 5.
- Referee: a test that enumerates all 120 permutations for L = 5 and requires 8.33 %; a wrong implementation (e.g. one-sided test -> different value, exact permutation p -> <= 5 %) fails.
- Afternoon extension with real novelty: the paper says random order is only a lower bound because fast neurons fire first.
  Null model "order by firing rate" (rate correlated with template position at rho = 0, 0.3, 0.6): answer key e.g. "FP rate at rho = 0.3 and L = 8 is above 10 %"; record the prediction before the run.
- Data: purely synthetic.
  No download.

### B. Does PCA really fail to find overlapping assemblies while ICA succeeds? (feasibility: high)

- Question: Check the claim from 2e ("even when assemblies have overlapping member neurons [...] a situation in which PCA fails") and the Marchenko-Pastur count from 2d.
- Setup: N = 50 Poisson neurons, B = 18 000 bins (30 min at 100 ms), K = 3 planted assemblies with 0 %, 25 %, 50 % member overlap.
- Answer key (proposal): (1) Null without assemblies: 0 significant components in >= 95 of 100 seeds; lambda_max = (1 + sqrt(50/18000))^2 = 1.108 (±0.001).
  (2) Planted K = 3: exactly 3 significant components in >= 95 % of seeds.
  (3) At 50 % overlap: mean |cosine similarity| between estimated and true assembly weights ICA >= 0.9, PCA < 0.8.
- Referee: lambda_max analytically; the null case must return 0; an error such as missing z-scoring or covariance instead of correlation shifts the eigenvalues and fails.
- Data: synthetic; optional validation on the DANDI 000044 MAZE epoch.

### C. Does a pure firing-rate change PRE -> POST create apparent reactivation (EV > REV)? (feasibility: high synthetic, medium with real data)

- Question: The analysis the paper calls "still missing" (3b-v): how much of EV - REV can arise from a rate change alone, and does rate matching (spike subsampling, [15]) remove the effect?
- Setup: neurons with a fixed shared input structure (e.g. thresholded Gaussian, where correlation rises with rate, De La Rocha 2007); POST: rates of the cells active during wake scaled up, coupling unchanged. Positive control: planted reactivation.
- Answer key (proposal): confound "verified" if EV - REV >= 0.05 (5 percentage points of explained variance) in >= 95 of 100 seeds with the rate change alone; correction "verified" if |EV - REV| < 0.02 after rate matching.
- Referee: the positive control must give EV - REV >= 0.10; the null without any change must give |EV - REV| < 0.02; the EV formula checked against a hand calculation on a 3x3 example.
- Data: synthetic; stretch: EV/REV with and without rate matching on one DANDI 000044 session (stream the units).

### D. How strongly does replay detection depend on bin size? (feasibility: medium-high)

- Question: The second explicit gap (3b-v): systematic variation of bin size for Bayesian decoding + weighted correlation / Radon.
- Setup: synthetic linear-track place fields (e.g. 60 cells, lognormal in-field rates), replay events with known compression plus noise spikes as in Fig. 4; bin sizes 5, 10, 20, 30, 40, 50 ms; null events via cell-identity shuffle.
- Answer key (proposal): bin dependence "verified" if the true-positive rate varies by >= 20 percentage points between 10 ms and 40 ms while the FP rate stays at 5 % ± 2 pp.
- Referee: perfect, noise-free events must be detected at >= 95 % for all bin sizes; pure shuffles <= 7 %; the decoder must hit the analytical posterior maximum for a single-cell example.
- Data: synthetic.
  Risk: more implementation (decoder + 2 goodness measures + shuffles) than A-C.

### E. Do the method agreements from Fig. 3 replicate on the Grosmark dataset? (feasibility: medium to low in 2-3 h)

- Question: The paper claims the low agreements also hold on [30] = DANDI 000044 but does not show it.
  Does R(rank-order, weighted correlation) of about 0.13 and R(weighted correlation, Radon) of about 0.43 hold there too?
- Setup: one session (Buddy, 1.6 m linear), stream only units + position; place fields from MAZE; candidate events from population bursts (without LFP ripple detection, to save download); >= 6 cells with exactly one field as in the paper.
- Answer key (proposal): "verified" if R(RO, WC) <= 0.30 and R(WC, Radon) - R(RO, WC) >= 0.15 over all candidate events; "contradicted" if R(RO, WC) >= 0.5.
- Referee: a positive control with synthetic perfect events must give R >= 0.8 for all three method pairs (otherwise the pipeline is wrong, not the biology).
- Data: DANDI 000044 (CC-BY-4.0).
  Risks: NWB structure, event detection without LFP deviates from the paper, network and time; shared machine, so streaming instead of a 5-10 GB download.

### Ranking

| Rank | Candidate | First result | Novelty | Risk |
|---|---|---|---|---|
| 1 | A rank-order FP (+ rate null) | < 30 min | medium (extension: high) | very low |
| 2 | C EV/REV rate confound | < 1 h | high (named as open by the paper) | low |
| 3 | B PCA vs. ICA + MP | < 1 h | low-medium (confirms known claims) | low |
| 4 | D bin size | 1-1.5 h | high (named as open by the paper) | medium |
| 5 | E Fig. 3 replication on DANDI 000044 | 1.5-2.5 h | high (real data, unshown claim) | high |

Combination option: A or C as the safe core until 16:00, E only as a stretch with a clearly marked "not enough evidence" if time runs out.

## 6. Recommendations

- Choose a question with a published or analytical anchor; the judge rewards verified negative results more than unsupported positive ones.
- Phrase the answer key directly as the `/goal` condition (number, unit, tolerance).
- Reimplement in Python instead of porting RnR_methods (GPL); cite the paper and the toolbox under "Data and sources".
- Synthetic data first, real data (DANDI 000044, streamed) only as a stretch.
- Plan the demo for 3 minutes; file the submission issue before 17:00 with links to JOURNAL.md and the result files.
