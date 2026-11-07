# Papers

Core papers for this project, with links and license status.
A PDF is committed here only when its license verifiably allows redistribution.
Everything else is linked, not copied.
This repository follows the lab licensing: text CC BY 4.0, code Apache 2.0.

License status was checked on 2026-11-07 against the Crossref license metadata, the Europe PMC record and the PMC article page.

## Tingley and Peyrache (2020), anchor paper

Tingley D., Peyrache A. (2020).
On the methods for reactivation and replay analysis.
*Philosophical Transactions of the Royal Society B: Biological Sciences* 375(1799): 20190231.
Theme issue "Memory reactivation".
Published 2020-04-06 by The Royal Society.

- DOI: [10.1098/rstb.2019.0231](https://doi.org/10.1098/rstb.2019.0231)
- Publisher: <https://royalsocietypublishing.org/doi/10.1098/rstb.2019.0231>
- PMC: [PMC7209909](https://pmc.ncbi.nlm.nih.gov/articles/PMC7209909/)
- PubMed: [32248787](https://pubmed.ncbi.nlm.nih.gov/32248787/)
- Reference code: [DavidTingley/RnR_methods](https://github.com/DavidTingley/RnR_methods) (MATLAB, GPL-3.0)

**License: all rights reserved, not committed.**
The PMC copyright line reads "© 2020 The Author(s) Published by the Royal Society. All rights reserved."
Europe PMC lists no open license and marks the article as not open access.
Crossref lists only the Royal Society text-and-data-mining policy, not a Creative Commons license.
The full text is free to read at the links above, but free to read is not free to redistribute, so the PDF is not stored in this repository.
Our [briefing](../briefing.md) quotes short passages with section references for discussion, which is not a copy of the article.

The reference toolbox is GPL.
Copying or porting its code would put this repository under GPL, so we reimplement methods from the formulas in the paper and only cite the toolbox.

## Takigawa et al. (2024)

Takigawa M., Huelin Gorriz M., Tirole M., Bendor D. (2024).
Evaluating hippocampal replay without a ground truth.
*eLife* 13: e85635.

- DOI: [10.7554/eLife.85635](https://doi.org/10.7554/eLife.85635)
- Publisher: <https://elifesciences.org/articles/85635>
- PMC: [PMC11666237](https://pmc.ncbi.nlm.nih.gov/articles/PMC11666237/)
- PubMed: [39606951](https://pubmed.ncbi.nlm.nih.gov/39606951/)
- Companion code: [bendor-lab/replay_detection_cross_validation](https://github.com/bendor-lab/replay_detection_cross_validation) (MATLAB, CC0-1.0)

**License: CC BY 4.0, committed.**
Crossref lists <http://creativecommons.org/licenses/by/4.0/> for the version of record, and Europe PMC lists the license as "cc by".
CC BY allows redistribution with attribution, which the citation above provides.
File: [2024_Takigawa_evaluating_replay_without_ground_truth.pdf](2024_Takigawa_evaluating_replay_without_ground_truth.pdf).

## Further papers

The wider reading list is in the [research README](../README.md#papers).
Those papers are linked only.
`research/scripts/fetch_sources.sh` downloads open-access full text into the git-ignored `research/_fetched/` folder for local reading.
