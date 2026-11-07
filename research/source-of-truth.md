# Source of truth: Tingley & Peyrache (2020)

Canonical method specification for the toolbox and the referee tests.

**Paper:** Tingley D., Peyrache A. (2020) "On the methods for reactivation and replay analysis".
Phil. Trans. R. Soc. B 375: 20190231.
DOI [10.1098/rstb.2019.0231](https://doi.org/10.1098/rstb.2019.0231).
Theo Murphy meeting issue "Memory reactivation: replaying events past, present and future".

**Supplementary information (SI):** "Supplementary Information from On the methods for reactivation and replay analysis", figshare collection DOI [10.6084/m9.figshare.c.4874646](https://doi.org/10.6084/m9.figshare.c.4874646) (file `rstb20190231supp1`, 6 pages).

**Code named by the paper:** "Replay and reactivation methods, as well as simulations, are available in the RnR_methods toolbox" (Data accessibility): https://github.com/DavidTingley/RnR_methods.
The paper's phrase "see the online simulations" points there.
That repository was not read for this document.

**License:** the article is "All rights reserved".
This file paraphrases and quotes only short phrases with section references.
No PDF, figure image or long passage is committed.

## How this file was produced and how far to trust it

- Main text read on 2026-11-07 from the publisher's full-text HTML in a logged-in browser session.
- Main-text equations were taken from the page's MathML, so their symbols are exact.
- SI read from the publisher-served SI PDF, as text and as rendered page images, so SI equations were checked visually.
- Figure numbers were read from the publisher's medium-resolution figure images.
  Anything read off a figure axis or colour bar is marked "(fig, approx.)".
- Where the paper's own notation is inconsistent or has a typo, the formula is reproduced as stated and the problem is flagged under "Notes on the formula".
  Nothing was silently corrected.
- Anything that is not in the paper but is needed to implement a method is listed in [What is not in the paper](#what-is-not-in-the-paper-toolbox-must-choose) and is never presented as the paper's claim.

### Section map

| Ref | Section title |
| --- | --- |
| §1 | Introduction |
| §2a | Cell-pair correlation and explained variance |
| §2b | Tracking reactivation over time |
| §2c | Principal component analysis |
| §2d | Determining the number of significant principal components |
| §2e | Other decomposition of neuronal data: independent component analysis and beyond |
| §3 | Replay methods (intro) |
| §3a | Cross-correlograms |
| §3b | Template-based approaches (intro) |
| §3b(i) | Template correlation analysis |
| §3b(ii) | Rank-order correlations |
| §3b(iii) | The Bayesian approach |
| §3b(iv) | Comparisons and general problems with template-based methods |
| §3b(v) | General problems with reactivation and replay methods |
| §4a | Unifying current methods |
| §4b | Template-free approaches |
| §5 | Generalized assembly detection: what is the "relevant" pattern? |
| SI | Supplementary information: Reactivation, Explained Variance, Reactivation strength, Bayesian decoding, General replay caveats, Template free methods (seqNMF), Dataset details |

### Vocabulary as the paper uses it

- **Reactivation:** methods that "quantify zero-lag relationships without examining temporal evolution" (Abstract).
- **Replay:** methods that "quantify the temporal structure of changing activity patterns" (Abstract).
- **PRE / behaviour (W, wake) / POST:** the standard within-animal paradigm: home-cage sleep for several hours, exposure to a new environment or maze, then home-cage sleep for several more hours; PRE is "an internal control to determine if such activity patterns were pre-existing" (§1).
- **Cell-pair coherence:** the correlation of cell-pair correlations between two epochs (§2a).
- **Reference epoch / target (test) epoch:** the epoch the components are learned from, and the epoch they are projected onto (figure 2 caption).

## Shared preprocessing (SI "Reactivation")

Binned spike-count matrix, rows are neurons and columns are time bins, as stated:

$$
A = \begin{matrix} a_1(1) & a_1(t) & a_1(B) \\ a_i(1) & a_i(t) & a_i(B) \\ a_N(1) & a_N(t) & a_N(B) \end{matrix}
$$

- $a_i(t)$: number of spikes of neuron $i$ in time bin $t$; $N$ neurons; $B$ time bins.
- Bold $\mathbf{a}(t)$: the population vector at bin $t$.

Z-scoring, done "during each epoch", as stated:

$$
z_i(t) = \frac{a_i(t) - \mu_a}{\sigma_a}
$$

- $\mu_a$, $\sigma_a$: mean and standard deviation of the spike count of neuron $i$.
- Stated reason: firing rate and spike-count variance are log-normally distributed, and "Covariance would give too much weight to high firing neurons" (SI).

Correlation matrix of an epoch, as stated:

$$
C_{epoch} = \frac{1}{B} Z^T Z
$$

**Notes on the formula.**
With $A$ (and therefore $Z$) laid out as $N \times B$, $Z^T Z$ is $B \times B$, not the $N \times N$ cell-pair matrix the text describes.
The intended object is the $N \times N$ neuron correlation matrix; the transpose placement is a notational inconsistency in the SI.
The SI does not say whether $\sigma_a$ is the population or sample standard deviation; $\frac{1}{B}$ matches the population form.

## Method specifications

Each block gives: formula as stated, inputs, parameters with the values the paper gives, assumptions, failure modes the paper names, and the section reference.
"Not stated" means the paper gives no value.

### M1. Cell-pair correlation (pairwise co-firing)

- **Source:** §2a, after Wilson & McNaughton [9].
- **Formula:** Pearson correlation between two binned spike-count vectors (§2a, no equation given).
- **Inputs:** spike trains of simultaneously recorded neurons, per epoch.
- **Parameters:** bin size "typically in the range 10–100 ms" (§2a).
- **Original reactivation readout:** "the difference in POST correlations between cell-pairs of overlapping or non-overlapping place fields" (§2a).
- **Failure modes named (§2a):**
  - it "only indirectly reflects the relationship between the cell-pair correlations during wakefulness and sleep";
  - it does not "account for the prior relationship between wake correlation and sleep PRE".
- **General rate confound:** "the correlation between two spike trains is a function of the firing rate of the two neurons, independent of the actual amount of shared inputs" (§3b(v), [14]).

### M2. Cell-pair coherence, explained variance (EV) and reverse explained variance (REV)

- **Source:** §2a; SI "Explained Variance"; partial-correlation form from [11], name EV from [12], REV from Pennartz et al. [13].
- **Cell-pair coherence, as stated (SI):**

$$
r_{1,2} = \frac{1}{N_{pairs}} \rho_1^T \rho_2
$$

  - $\rho_{1,2}$: "the z-scored vector of all cell-pair correlation coefficients during epochs 1 and 2".
  - $N_{pairs}$: total number of cell pairs, "i.e. N(N-1)/2".
- **EV, as stated (main text MathML, identical in SI):**

$$
EV = \left( \frac{r_{W,POST} - r_{W,PRE}\, r_{PRE,POST}}{\sqrt{\left(1 - r_{W,PRE}^2\right)\left(1 - r_{PRE,POST}^2\right)}} \right)^2
$$

  - $r_{A,B}$: cell-pair coherence between epochs A and B; W is the behaviour (wake) epoch.
  - EV is the squared partial correlation of wake-POST coherence given wake-PRE (and PRE-POST) coherence.
- **REV:** "obtained by switching epochs PRE and POST in the above equation" (SI), i.e. "the 'flow' of time is reversed" (§2a).
- **Decision rule stated:** "Reactivation can thus be assessed by a significant difference between EV and REV across recording sessions" (§2a).
  The statistical test is not named.
- **Inputs:** binned spike trains of PRE, W, POST; same neurons in all three.
- **Parameters:** bin size as M1 (10–100 ms, §2a).
  Number of neurons, minimum pairs: not stated.
- **Assumptions:** a "forward" flow of time from PRE to POST (§2a).
- **Failure modes named (§2a):**
  - "EV by itself does not have any measure for the degree of variability (i.e. noise) across correlations" and "is not compared to a proper control" (addressed by REV).
  - "it does not account for the possible change in firing rates (independent of correlations) that inevitably leads to changes in correlation".
    Proposed controls: "subsampling spike trains to equalize rates [15]", or "greatly increase the time bin size in order to estimate the contribution of slow time-scale rate fluctuations".
  - "it does not allow for the resolution of reactivation in time" (one value per sleep epoch).
  - "all cell-pair correlation values are considered, not controlling for the fact that data of limited duration inevitably generates non-zero correlations".

### M3. Reactivation strength (projection onto a correlation matrix)

- **Source:** §2b; SI "Reactivation strength".
- **Cell-pair coherogram, as stated (SI):**

$$
\chi_{sleep}(t) = \mathbf{z}_{sleep}^T(t)\, C_{wake}\, \mathbf{z}_{sleep}(t)
$$

  - $\mathbf{z}_{sleep}(t)$: one time bin (population vector) of the z-scored sleep matrix (SI calls it "a row").
  - "The time average of the coherogram is equal to the variance during the sleep epoch explained by the correlation of the wake epoch" (SI).
  - Coherence and coherogram "are related, they are not exactly similar" (SI).
- **General reactivation strength, as stated (main text):**

$$
R_{sleep}(t) = z_{sleep}^T(t)\, P_{wake}\, z_{sleep}(t)
$$

  - "P is a projector (in the simplest case, the correlation matrix) with diagonal elements equal to 0" (§2b).
- **Inputs:** z-scored binned spike trains of the reference epoch (to build $P$) and of the target epoch (to project).
  "this method applies to any pairs of recording epochs" (SI).
- **Parameters:** bin size not stated for this method specifically; figure 2 example uses a 25 min reference and a 25 min test epoch with 37 neurons (fig, approx.).
- **Assumptions:** z-scored products of spike counts are comparable to correlation values because "a correlation value between any two variables is the average of the product of their z-scored values" (§2b).
- **Failure modes named:**
  - "strongly sensitive to the firing of individual neurons"; fix: "the diagonal of the matrix can be set at 0" (§2b).
  - Using the full correlation matrix "does not address the possibility that noisy correlations can potentially overshadow the actual signal, or at least diminish dramatically the effect size" (§2b); this motivates M4 and M6.
  - A single-instance template (M8 style) instead of an average correlation "is prone to high level of noise" (§2b).

### M4. PCA reactivation strength (per-component projectors)

- **Source:** §2c, figure 2, SI "Reactivation strength"; method of [45,51].
- **Eigendecomposition, as stated (SI):** $C v_i = \lambda_i v_i$, and

$$
C = \sum_{i=1}^{N} \lambda_i P^i, \qquad P^i = v_i v_i^T
$$

- **Diagonal removal (SI):** "the diagonal of the projectors is set at 0" ($P_{k,k}=0$).
- **Per-component reactivation strength, as stated (SI):**

$$
R^i(t) = \mathbf{z}_{sleep}^T P^i \mathbf{z}_{sleep}(t)
$$

  which "by expanding all the terms is equal to":

$$
R^i(t) = \sum_{k \neq l} v_k^i v_l^i z_k(t) z_l(t)
$$

- **Component selection:** keep "only a subset of projectors (corresponding to vectors explaining more variance than expected from random data)" (SI); the count comes from M5.
- **Pipeline (figure 2 caption):** reference epoch → bin → correlation matrix → eigenvectors → count eigenvalues above $\lambda_{max}$ → projectors (outer products of significant PCs or of ICs) with zero diagonal → bin and z-score target epoch → project → $R(t)$ per component.
- **Inputs:** reference-epoch and target-epoch spike trains, same neurons.
- **Parameters:** bin size not stated for this method; figure 2 example has 3 significant components out of 37 neurons (fig, approx.).
- **Assumptions:** PCs are eigenvectors of the correlation matrix; each eigenvalue equals "the total variance explained by this combination of inputs" (§2c).
- **Failure modes named (§2d):** "it forces components to be orthogonal to each other (by construction)" and "may not identify properly the assemblies of neurons that are coordinated [53]".
  Figure 4b(i) shows PCA reactivation strength degrading as real spikes are removed and noise spikes added.

### M5. Number of significant components: eigenvalue null and Marchenko-Pastur bound

- **Source:** §2d, figure 2.
- **Statement:** keep "PCs that explain variance exceeding what is expected from random data (i.e. independently firing neurons)" (§2d).
- **Two "equivalent approaches" (§2d):**
  1. Shuffle "the data (bin-to-bin for each cell)" to get a null distribution of eigenvalues and its upper bound.
  2. Use the Marchenko-Pastur distribution "of eigenvalues expected for random datasets"; any PC above the theoretical upper bound $\lambda_{max}$ "can be considered significant with almost absolute certainty".
- **Formula for $\lambda_{max}$:** **not given in the paper or the SI.** See the not-in-paper list.
- **Facts stated (§2d):**
  - The total variance of a correlation matrix "is the number of variables".
  - For "an infinite-long recording of independently firing neurons" the correlation matrix is the identity and every eigenvalue is 1.
  - Finite recordings give "a spectrum of eigenvalues that is distributed around 1, with a width depending on the number of variables (i.e. neurons) and time bins".
  - The spectrum "is sharply bounded"; "a small correction for finite data is possible but is generally negligible".
  - During active wakefulness (asynchronous state), "cell-pair correlations remain low and distributed around 0 [52]", so eigenvalues are "narrowly distributed around 1", and explained-variance-percentage rules ("the first n PCs explain X% of the variance") are not useful.
- **Shuffle count and percentile:** not stated.

### M6. ICA reactivation (assembly patterns)

- **Source:** §2e, figure 2; method of [20], used in [15,21].
- **Procedure as stated:** "ICA is performed on the data projected onto the subspace of the significant components (as determined from the spectrum of eigenvalues) to de-mix the PCs into independent components" (§2e).
  The IC projectors replace the PC projectors in M4 (figure 2 caption).
- **Formula:** no ICA equation and no ICA algorithm is given.
- **Inputs, parameters:** as M4 and M5.
- **Properties claimed (§2e):**
  - On artificial spike trains ICA "successfully separates assemblies of coordinated neurons, even when assemblies have overlapping member neurons [20], a situation in which PCA fails".
  - "The overall variance explained ... by ICA can be less than with PCA, yet the ICA may be more suitable to track the activation time course of a given assembly (and be potentially more interpretable)".
- **Failure modes:** figure 4b(ii) shows ICA reactivation strength also degrades with removed real spikes and added noise spikes.
- **Alternatives mentioned:** dimensionality-reduction alternatives [55]; PCA generalised to the exponential family, "including binary and Poisson distributed data" [56] (§2e).

### M7. Cross-correlogram (CCG) asymmetry

- **Source:** §3a; SI "General replay caveats"; method of Skaggs & McNaughton [18].
- **CCG:** computed "By iteratively shifting in time (±200 ms) and correlating pairs of spike trains" (§3a).
- **Asymmetry index, as stated (MathML):**

$$
B_{ij} = \int_0^{200} x_{ij}(t)\, dt - \int_{-200}^{0} x_{ij}(t)\, dt
$$

  - $x_{ij}(t)$: the CCG of cells $i$ and $j$ at lag $t$ (ms implied by the ±200 ms window).
- **Readout:** compute $B_{pre}$, $B_{behav}$, $B_{post}$ per epoch; replay is inferred when $B_{behav}$ and $B_{post}$ "should be more correlated" than $B_{behav}$ and $B_{pre}$ (§3a).
- **Inputs:** spike trains for all pairs in PRE, behaviour, POST.
- **Parameters:** lag window ±200 ms (§3a).
  CCG bin size, normalisation and smoothing: not stated.
- **Assumption:** replay must occur "more than expected when compared to either a random generative process or the previously existing internal dynamics of the network" (§3a).
- **Failure modes named:**
  - "susceptible to issues arising from data processing, data inclusion, and firing rate distributions" (§3a, details in SI).
  - Spike-sorting: bursts with changing waveforms may be "misidentified as two or multiple neurons firing in close temporal order"; because only "~5%" of CCGs show the asymmetry, "even very rare mistakes in clustering waveforms can impact the results greatly" (SI, citing Quirk & Wilson 1999).
    Mitigation: "only examine cell pairs recorded across separate tetrodes/shanks" (SI).
  - Firing-rate distribution: a small fraction of high-rate neurons can bias results; mitigation: "Z-scoring or generating bootstrapped firing rate matched distributions for comparison" (SI).

### M8. Template correlation with scaling factor

- **Source:** §3b(i); method of Louie & Wilson [16] and Lee & Wilson [22]; later used in prefrontal cortex [40] and forebrain [39].
- **Template:** behaviour-epoch firing-rate maps, "typically over spatial bins of a maze or environment" (§3b).
- **Template correlation, as stated (MathML):**

$$
C_t = \frac{1}{\sigma_x \sigma_y} \frac{1}{N \cdot C} \sum_{c=1}^{C} \sum_{n=1}^{N} \left( \frac{x_{nc}}{X_c} - \bar{x} \right) \left( \frac{y_{nc}}{Y_c} - \bar{y} \right)
$$

  - $x_{nc}$, $y_{nc}$: "the binned smoothed spike counts for cell c at time n across two different epochs".
  - $C$: number of cells; text says "n is the number of bins" while the formula sums to $N$.
  - $\bar{x}$, $\bar{y}$: "the average bin values for the two epochs".
  - $X_c$, $Y_c$: "the root mean square of the bin values".
- **Scaling factor:** warp the behavioural template "with different temporal scales (0.5 to 20-fold)"; report the correlation and "the scaling factor of the template with the highest correlation" (§3b(i)).
  Implemented by "varying the time bin size for one of the two spike trains X or Y relative to the other".
- **Parameters:** scale range 0.5–20-fold (§3b(i)); smoothing kernel and base bin size: not stated.
- **Assumption:** the template-to-event mapping is linear, "a scalar multiplication" (§3b(ii)).
- **Failure modes named:** "if replay sequences are flexible, dynamically adjusting the rate of change within a given event, this linearity assumption could severely impede our ability to detect and quantify such events" (§3b(ii)); temporal-scale mismatch between behaviour and sleep (§3b).
- **Notes on the formula:** $\sigma_x$, $\sigma_y$ are not defined in the text; $N$ vs "n is the number of bins" is a notation clash.

### M9. Rank-order correlation

- **Source:** §3b(ii); used by [23,24]; predecessor: Lee & Wilson combinatorics [22].
- **Procedure:** "compares only the order in which place fields fire on a maze with the ordering of spikes within a given candidate replay event"; their correlation quantifies sequence similarity "while disregarding precise temporal structure" (§3b(ii)).
- **Formula:** not given; the correlation type (for example Spearman) is not named.
- **Predecessor:** Lee & Wilson [22] "used combinatorics to determine the 'true' probability to observe the sequence of a candidate replay event knowing the order of firing during exploration"; first report of sleep replay of sequences "greater than three neurons"; "For some reasons, this method was then replaced by simpler approaches" (§3b(ii)).
- **Inputs:** template order (place-field order on the maze), spikes per cell within a candidate event.
- **Parameters:** in the paper's comparison, templates needed "a minimum of at least six place cells with only one field" (§3b(iv)); events needed "at least 5 place cells" with at least one spike each (SI).
  Spike inclusion "(first or all)" is listed among the choices that differ across papers (§3b(iv)).
- **Failure modes named:**
  - Multi-field neurons create ambiguity ("Should a neuron be ordered by its more reliable field? The higher firing rate field? Should it be included twice?"); "Typically, such neurons are excluded" (§3b(ii)).
  - More susceptible to single "gaps" in a trajectory than weighted distance correlation (§3b(ii)).
  - False positives on random data: 5–12% for length-10 sequences and up to 20% for length 5 (see anchors A36-A37) (§3b(iv)).
  - Event detection that relies on silence then a population burst favours faster-firing neurons firing first [66] (§3b(iv)).
  - Figure 4a(i): sensitive to added noise spikes and removed real spikes.

### M10. Weighted distance correlation

- **Source:** §3b(ii), Liu, Grosmark & Chen [57].
- **Statement:** "While not strictly a 'rank-order' correlation", it "is also capable of capturing similar ordinal relationships without relying on linear relationships between templates and candidate events" (§3b(ii)).
- **Property claimed:** "far less susceptible to single 'gaps' in a replay trajectory than the rank-order correlation, or weighted correlation ... methods" (§3b(ii)).
- **Formula, inputs, parameters:** not given in the paper.
  Not part of the paper's figure 3 comparison.

### M11. Bayesian decoding

- **Source:** §3b(iii), SI "Bayesian decoding"; framework of Zhang et al. [58].
- **Occupancy prior, as stated (SI):**

$$
P(x) = \frac{N(x)}{\sum_x N(x)}
$$

  $N(x)$: "the number of times the animal occupied position $x$".
- **Rate map, as stated (SI):**

$$
f(x) = \frac{S(x)}{N(x)\Delta t}
$$

  $S(x)$: total spike count at location $x$; $N(x)\Delta t$: total time spent at $x$.
- **Posterior, as stated (main text MathML, identical in SI image):**

$$
P(x \mid n) = P(x) \left( \prod_{i=1}^{N} f_i(x)^{n_i} \right) \exp\left( -\tau \sum_{i=i}^{N} f_i(x) \right)
$$

  - $f_i(x)$: average firing rate of neuron $i$ at position $x$; $n_i$: spike count of neuron $i$ in the window; $\tau$: window length.
  - $P(x)$ is "the normalized occupancy map" (§3b(iii)).
- **Use for replay:** decode each bin of a candidate event to get "a posterior probability matrix"; then fit a line to score it, "assuming that replay should consist of a continuous trajectory across time bins" (§3b(iii)).
- **Parameters (§3b(iii)):** bins τ of "10–50 ms"; posterior matrix spans "approximately 50–500 ms".
  Variant: fixed number of spikes per bin, variable bin size [32]; "should lead, by construction, to higher and more homogeneous posterior probability of decoding, it gives similar results to fixed-time bin methods".
- **Assumptions:** uses an average rate map per neuron, so it is also a template method (§3b(iii)).
- **Failure mode named (SI worked example):**
  two non-overlapping place cells with peak rates 50 Hz and 25 Hz and similar reliability each fire one spike in one bin.
  With 20 ms bins one spike is 50 Hz and the decode goes to cell 1; with 50 ms bins it is 20 Hz and the decode goes to cell 2.
  "the estimated position is based solely on the choice of temporal bin size", and "the trial-by-trial spatial reliability of cells is not a factor" (SI).
- **Robustness claim:** the probabilistic approach "can be much more robust" to multi-field ambiguities than rank-order (§3b(ii)).
- **Notes on the formula:**
  - The summation index reads "$i = i$" in both the main text and the SI; read as $i = 1$.
  - The posterior is written with "=" but has no normalising constant over $x$, so it is proportional to the posterior.
  - $n$ is overloaded in §3b(iii): "for n neurons" and "the number of spikes n"; the formula uses $N$ neurons and spike counts $n_i$.

### M12. Radon transform line fit

- **Source:** §3b(iii) [27]; figure 3d,e.
- **Statement:** one of "two common ways to quantify this posterior probability matrix" (§3b(iii)).
- **Outputs used in figure 3:** "the integral of the line of best fit" and "the slope of the line of best fit, using the radon transform method".
- **Formula and parameters** (line band width, slope and intercept search range, handling of empty bins): not given.
- **Failure mode:** figure 4a(ii) shows the radon integral changing with added noise and removed real spikes; colour scale spans about 0.03–0.05 (fig, approx.).

### M13. Linear weighted correlation

- **Source:** §3b(iii) [60]; figure 3b-d.
- **Statement:** the other common way to score the posterior matrix (§3b(iii)); figure 3b reports "R-values are the linear weighted correlations between each event and the template generated from maze traversals".
- **Formula:** not given.
- **Range:** the figure 3b histogram spans −1 to 1, with example events at R = −0.85, −0.19, −0.07, 0.18, 0.82 (fig).

### M14. Template-free approaches

- **Source:** §4b; SI "Template free methods".
- **Idea:** capture reliable patterns during behaviour without a behavioural template, compare with PRE or POST, and "warped in time to assess compression or expansion" (§4b).
- **seqNMF, as stated (SI), after Mackevicius et al. [62]:**

$$
X_{nt} = \sum_{k=1}^{K} \sum_{l=0}^{L-1} W_{nkl} H_{k(t-l)} \equiv (W * H)_{nt}
$$

  - $X_{nt}$: neuron $n$, time bin $t$.
  - $W$: "a N x K x L tensor containing 'exemplar' patterns"; $K$ patterns and length $L$ both "defined a priori".
  - $H$: "a K x T matrix of temporal loadings".
  - A penalty $R$ "that accounts for both correlations between temporal loadings and correlations between different patterns in W" gives an algorithm that "reliably converges on a similar result across random initializations"; the form of $R$ is not given.
- **Other families named (§4b):** decomposing population time series [62], clustering neural patterns [73,74], estimating neural states [31,75], deep learning that captures single-trial statistics [76].
- **Failure mode named:** "the experimenter may not have a good idea what the observed patterns are best related to in terms of the animals' behaviour or state (i.e. we may be unable to ground such relations to anything meaningful)" (§4b).
- **Related template problem (§3b(iv)):** templates do not generalise to "non-spatial features of experience", and without measuring everything, "one cannot conclude that a candidate replay event is not 'replaying' something the experimenter did not measure"; unsupervised methods [31,43,62] show "promising early results".

## Referee anchors: every quantitative claim

Read quality: "exact" means copied from text or MathML; "(fig, approx.)" means read from a medium-resolution figure image.
IDs are stable so tests can cite them.

| ID | Claim | Value | Where | Read quality |
| --- | --- | --- | --- | --- |
| A01 | Pavlides & Winson first showed experience affects hippocampal sleep activity | 1989, "Thirty years ago" | §1 | exact |
| A02 | Ripple oscillation frequency | 100–200 Hz | §1 | exact |
| A03 | Standard paradigm: home-cage sleep before and after maze | "several hours" each | §1 | exact |
| A04 | Bin size for cell-pair correlations | 10–100 ms typical | §2a | exact |
| A05 | Number of cell pairs | $N(N-1)/2$ | SI | exact |
| A06 | Projector diagonal | set to 0 ($P_{k,k}=0$) | §2b, SI, fig 2 | exact |
| A07 | Eigenvalues of an infinitely long independent recording | all equal 1; matrix is identity | §2d | exact |
| A08 | Total variance of a correlation matrix | equals the number of variables (neurons) | §2d | exact |
| A09 | Width of the finite-data eigenvalue spectrum | depends on number of neurons and of time bins | §2d | exact |
| A10 | Finite-data correction to the Marchenko-Pastur bound | "generally negligible" | §2d | exact |
| A11 | Above-bound PCs are significant | "with almost absolute certainty" | §2d | exact |
| A12 | Awake asynchronous-state pair correlations | "low and distributed around 0"; eigenvalues "narrowly distributed around 1" | §2d | exact |
| A13 | ICA separates overlapping assemblies where PCA fails | on artificially generated spike trains [20] | §2e | exact |
| A14 | ICA explained variance vs PCA | "can be less than with PCA" | §2e | exact |
| A15 | Bin size for zero-lag (reactivation) methods | 10–200 ms | §3 intro | exact |
| A16 | CCG lag window | ±200 ms | §3a | exact |
| A17 | Asymmetry index integration limits | 0 to 200 and −200 to 0 | §3a | exact |
| A18 | Fraction of CCGs that show temporal asymmetry | ~5% (Skaggs & McNaughton 1996) | SI | exact |
| A19 | Template scaling factors tested | 0.5 to 20-fold | §3b(i) | exact |
| A20 | Lee & Wilson multi-neuron sequences | "greater than three neurons" | §3b(ii) | exact |
| A21 | Bayesian bin size τ for candidate events | 10–50 ms | §3b(iii) | exact |
| A22 | Span of the posterior probability matrix | approximately 50–500 ms | §3b(iii) | exact |
| A23 | Fixed-spike-count bins vs fixed-time bins | "similar results" | §3b(iii) | exact |
| A24 | Comparison dataset | n = 39 recordings, n = 5 rats [61] | §3b(iv), fig 3a,b | exact |
| A25 | Rats | Long Evans, 3 male, 2 female | SI | exact |
| A26 | Session structure | PRE/behaviour/POST, each 1–5 hours | SI | exact |
| A27 | Templates | 54, all linear tracks | §3b(iv) | exact |
| A28 | Minimum cells per template | at least six place cells with only one field | §3b(iv) | exact |
| A29 | Place-field heuristics | min peak 2 Hz; min width 8 cm; max width 120 cm; min 1.5 spikes per trial on average; at least 10 trials with consistent behaviour | SI | exact |
| A30 | Candidate event criteria | SWRs from CA1 LFP; at least 5 place cells each firing at least one spike | SI | exact |
| A31 | Rank-order vs linear weighted correlation, event-by-event | average R = 0.126 across all sessions and templates | §3b(iv), fig 3c | exact |
| A32 | Linear weighted correlation vs radon | text: R = 0.43, "a greater degree of agreement"; figure 3d: 0.43 is versus radon **slope**, versus radon **integral** is avg. R = 0.194 | §3b(iv), fig 3d | text exact; figure split from fig |
| A33 | Rank-order vs radon | text: R = 0.07, "not significantly correlated"; figure 3e: 0.07 is versus radon **slope**, versus radon **integral** is avg. R = 0.003 | §3b(iv), fig 3e | text exact; figure split from fig |
| A34 | Method agreement under noise | "each replay and reactivation method was uniquely susceptible such that agreement across methods could be degraded" | §3b(iv), fig 4 | exact |
| A35 | Typical fraction of candidate events called significant by within-event shuffles | consistently 5–20% [23,25,27,30,60,63] | §3b(iv) | exact |
| A36 | Rank-order false positives, random sequence generator, length 10, against any random template | approximately 5–12% (n = 100 events) | §3b(iv) | exact |
| A37 | Rank-order false positives, length 5 | "can reach up to 20%" | §3b(iv) | exact |
| A38 | Random-sequence false-positive rate is a lower bound | neural activity occupies "a much smaller set of sequential patterns than pure randomness" [64,65] | §3b(iv) | exact |
| A39 | Silence before burst in event detection | "approx. 100 ms" | §3b(iv) | exact |
| A40 | Firing-rate range in typical recordings | approx. 0.001–100 Hz, lognormal | §3b(v) | exact |
| A41 | Typical bin sizes by field | reactivation approx. 50–200 ms; replay approx. 10–50 ms | §3b(v) | exact |
| A42 | Experiment duration | many hours (3–10) | §3b(v) | exact |
| A43 | Bayesian bin-size example | peaks 50 Hz and 25 Hz; 1 spike in 20 ms = 50 Hz decodes to cell 1; 1 spike in 50 ms = 20 Hz decodes to cell 2 | SI | exact |
| A44 | Fig 2 example | 37 neurons; reference and test epochs about 25 min each; 3 significant components; projection-matrix colour scale about ±0.2 | fig 2 | (fig, approx.) |
| A45 | Fig 3a example | about 120 cells over about 3.5 s of maze traversal | fig 3a | (fig, approx.) |
| A46 | Fig 3b example events | R = −0.85, −0.19, −0.07, 0.18, 0.82; event windows on the order of 120–160 ms; weighted-correlation histogram spans −1 to 1, peak count near 90 around 0 | fig 3b | R values exact from figure labels; rest (fig, approx.) |
| A47 | Fig 4 simulation setup | n = 100 cells, one spike each per event; "perfect" event: every cell fires one spike in template order; x: number of randomly inserted noise spikes, y: number of randomly removed real spikes | fig 4 caption | exact |
| A48 | Fig 4 axis ranges | both axes run 1 to 100; spacing looks logarithmic | fig 4 | (fig, approx.) |
| A49 | Fig 4a(i) rank order | colour scale 0 to 1.0; highest with few removed real spikes and few added noise spikes, lower as either increases | fig 4a(i) | (fig, approx.) |
| A50 | Fig 4a(ii) radon integral | colour scale about 0.03 to 0.05; high both at few removed real spikes and at many added noise spikes, lowest at many removed real spikes with few noise spikes | fig 4a(ii) | (fig, approx.) |
| A51 | Fig 4b reactivation strength (PCA, ICA) | colour scale about 0 to 10+; highest at few removed real spikes, near 0 at many removed; ICA lower and flatter than PCA at the top | fig 4b | (fig, approx.) |
| A52 | Same conclusions on other data | "Similar results were observed using simulated data and an alternative previously published dataset [30]" | §3b(iv) | exact; numbers not given |
| A53 | Brownian-diffusion replay | replay trajectories "matches the statistics expected from a fluid undergoing Brownian diffusion" [32] | §3b(iv) | exact |
| A54 | Bin size matters for template replay methods | "Preliminary simulations suggest bin size can greatly alter how some template-based replay detection methods perform" | §3b(v) | exact; numbers not given |

Not treated as anchors: funding grant numbers, figure 1 phylogeny (a qualitative lineage diagram of methods and citations), and citation years in the reference list.

**Text vs figure disagreement (A32, A33).**
The text attributes R = 0.43 to "the radon transform approach" and R = 0.07 to "the radon transform method" in general.
Figure 3d,e show those values are for the radon **slope**; the radon **integral** gives 0.194 and 0.003.
A referee test should pin the figure split, and should not assume that "radon" means one score.

## Null models, shuffles and controls in the paper

| Null or control | What it controls for | Where |
| --- | --- | --- |
| PRE epoch as internal control | patterns that were "pre-existing" before the experience | §1 |
| Partial correlation on wake-PRE coherence (EV) | prior similarity between wake and PRE correlation structure | §2a, SI |
| REV (swap PRE and POST) | gives EV a reference value, since EV alone "is not compared to a proper control"; tests the forward flow of time | §2a, SI |
| Subsampling spike trains to equalize rates [15] | firing-rate changes that change correlations independent of co-firing | §2a |
| Much larger time bins | contribution of slow time-scale rate fluctuations | §2a |
| Zero diagonal of projector | single-neuron rate fluctuations dominating reactivation strength | §2b, SI, fig 2 |
| Bin-to-bin shuffle per cell, eigenvalue null | eigenvalues expected from independently firing neurons of the same duration | §2d |
| Marchenko-Pastur bound | same as the bin-to-bin shuffle, analytically; called "equivalent" | §2d |
| Comparison of B_behav-B_post vs B_behav-B_pre correlation | sequence bias that existed before the experience | §3a |
| "random generative process or the previously existing internal dynamics" | chance sequences and pre-existing network sequences | §3a |
| Cell pairs from separate tetrodes or shanks only | spike-sorting errors creating false temporal order | SI |
| Z-scoring, or bootstrapped firing-rate-matched distributions | bias from the small fraction of high-rate neurons | SI |
| Within-event shuffles (types not enumerated) | event-level significance against shuffles of that event's own data; the paper says this alone cannot establish replay | §3b(iv) |
| Random sequence generator against random templates | rank-order false-positive rate by chance; the paper treats it as a lower bound | §3b(iv) |
| Proportion of significant events out of all candidates, compared with chance | experience-specific change in the network, rather than single-event significance | §3b(iv) |
| Same proportion in PRE vs POST | change in excitability and firing rates between PRE and POST shifts the false-positive rate [17] | §3b(iv) |
| Signal-to-noise simulation (insert noise spikes, remove real spikes) | per-method susceptibility and cross-method agreement | fig 4 |
| Same events through several methods | method dependence of replay calls | §3b(iv), fig 3 |

The paper does not give a shuffle count, a significance level or a percentile for any shuffle.

## Open gaps and recommendations, quoted

- "no two studies use the exact same approach, which prevents an unbiased comparison between findings" (Abstract).
- "These observations should instead be validated by multiple and, if possible, previously established tests" (Abstract).
- "the observation and quantification of such patterns depend intimately on the choice of methods used for detection and statistical assessment of their existence" (§1).
- "it remains unclear how well these methods would agree with one another" (§3b(iv)).
- "we were unable to find any two papers that used precisely the same data processing and analysis methods" (§3b(iv)).
- "the determination of which candidate replay events are significant 'replays' may depend on the method used, rather than the underlying neural activity pattern" (§3b(iv)).
- "It is not clear how such methods could be generalized to non-spatial features of experience" (§3b(iv)).
- "it is often unclear with these methods how many candidate events should be expected to appear as replays given chance" (§3b(iv)).
- "examining the proportion of significant events, out of all candidate events, is necessary" (§3b(iv)).
- "controlling for these potential confounding factors seems crucial to assess the validity of replay analyses" (§3b(iv)).
- "This raises the question of what constitutes replay of actual memories versus spontaneous and random exploration" (§3b(iv)).
- On rate-driven correlation change: "A systematic review and analysis of this possibility is still missing in the field" (§3b(v)).
- "most of the current methods can be heavily biased by a small subset of the fastest firing neurons" (§3b(v)).
- "a systemic variation of bin size and its impact on pattern detection is lacking" (§3b(v)).
- "circadian and metabolic effects on activity patterns have not been thoroughly examined within this paradigm" (§3b(v)).
- "it will be crucial for researchers to directly compare multiple methods" (§4a).
- "adopting a single community-developed code base and standardization [71], or further developing a taxonomy of methods [72]" (§4a).
- "Should two neurons with an order of magnitude difference in firing rate be treated the same?" (§5).
- "Can a post-synaptic neuron read-out (i.e. integrate) these spatio-temporal patterns which are often distributed across hundreds of milliseconds?" (§5).
- "We still do not know which, if any, mental state 'replay' corresponds to" (§5).
- "designing methods that behave like post-synaptic neurons or populations would be a fruitful perspective" (§5).

## What is not in the paper (toolbox must choose)

Every item below is **a toolbox decision, not the paper's claim**.
Where a pointer to a cited source is given, it is outside this paper and must be verified against that source before it is used.

1. **Marchenko-Pastur bound formula.**
   The paper names $\lambda_{max}$ but gives no formula, no aspect-ratio convention and no finite-size correction.
   The cited PCA method paper [51] (Peyrache et al. 2010) is the place to check.
2. **Eigenvalue-shuffle settings:** number of shuffles and the percentile used as the upper bound.
3. **ICA details:** algorithm, initialisation, seed, sign and scale normalisation of the weights, and how IC weights become projectors.
4. **Z-scoring edge cases:** neurons with zero variance in an epoch, and population vs sample standard deviation.
5. **Default bin sizes inside the stated ranges** (A04, A15, A21, A41), including which one each method uses.
6. **EV/REV session-level test:** the paper asks for "a significant difference between EV and REV across recording sessions" but names no test.
7. **Minimum cell counts for reactivation methods:** none stated.
   Only the replay comparison gives counts (A28, A30).
8. **Firing-rate equalisation:** the subsampling procedure is cited [15] but not specified.
9. **CCG details:** bin size, normalisation, smoothing, and the statistic used to correlate asymmetry indices across epochs.
10. **Template correlation details:** smoothing kernel, base bin size, definition of $\sigma_x$, $\sigma_y$, and the grid of scale factors inside 0.5–20.
11. **Rank-order correlation:** correlation type, first spike vs all spikes, tie handling, and how the template order is defined.
12. **Weighted distance correlation:** the whole formula [57].
13. **Linear weighted correlation:** the whole formula [60].
14. **Radon transform:** line parametrisation, band width, slope and intercept ranges, the exact "integral" and "slope" outputs.
15. **Bayesian decoding details:** spatial bin size, rate-map smoothing, zero-rate floor, occupancy prior vs uniform prior, and posterior normalisation.
16. **Candidate event detection:** ripple band, thresholds, durations and merging rules (the paper says only SWRs from CA1 LFP and at least 5 place cells).
17. **Within-event shuffle types, counts and significance level:** the paper says "various within-event shuffling methods" and names none.
18. **Chance-level proportion of replay events:** how to estimate the expected false-positive proportion across all candidates.
19. **Figure 4 simulation details:** spike timing of a "perfect" event, how noise spikes are placed, how reactivation strength is computed on a single event, and what reference epoch the PCA and ICA templates come from.
20. **Random-sequence false-positive simulation:** the significance threshold and correlation type behind A36 and A37.
21. **Cross-method agreement statistic:** figure 3c-e reports an event-by-event correlation averaged over sessions and templates; the correlation type and averaging are not specified.

## Notational issues found in the paper

| Where | Issue |
| --- | --- |
| SI, correlation matrix | $C_{epoch} = \frac{1}{B} Z^T Z$ with $Z$ laid out $N \times B$ gives a $B \times B$ matrix, not the $N \times N$ cell-pair matrix described |
| SI, z-score | $\mu_a$, $\sigma_a$ carry no neuron index although they are per neuron |
| §3b(i), template correlation | $\sigma_x$, $\sigma_y$ undefined; text says "n is the number of bins" while the formula sums to $N$ |
| §3b(iii) and SI, Bayesian posterior | summation index written "$i = i$"; posterior written with "=" without a normalising constant; $n$ used both for number of neurons and for spike counts |
| §3b(iv) vs figure 3d,e | the text's radon R values are the figure's radon-slope values; radon-integral values differ (A32, A33) |
| §2a vs §3 vs §3b(v) | reactivation bin size given as 10–100 ms, 10–200 ms and approx. 50–200 ms in different places |
| Figure 3 caption | "Cells are sorted and coloured to match figure 1a"; figure 1 has no panel a, so this presumably means figure 3a |
| Figure 2 caption | "reaction strengths (R)" for reactivation strengths |
