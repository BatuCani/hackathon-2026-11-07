# Skill scan: davidondrej/skills `research-and-web`

As of 2026-11-07, translated from the German original.
Scout pass: nothing installed, nothing copied.

**Result: nothing usable. Install nothing.**

- Repo state: `main` `c23d9026faad2a122b989e6faf54930e099bc19e` (2026-11-06T11:00:19Z, "Publish sanitized skills snapshot").
- Licence: MIT, Copyright 2026 David Ondrej (`LICENSE`); `browser-use` has its own MIT, Copyright 2024 Gregor Zunic (`browser-use/LICENSE.md`).
- Read with `gh-axi` (contents API, tree `?recursive=1`, code search): every `SKILL.md` under `skills/research-and-web/`, the referenced install, licence, script and `deepapi/references/*.md` files, then all 52 other `SKILL.md` files in the repo.

## The ten skills

| Skill | What | Verdict |
|---|---|---|
| browser-harness | CDP control of a running Chrome; needs `uv`, Chrome remote debugging, optional paid cloud key | skip, browser setup not needed; duplicate of `browser-use` |
| browser-use | Same CDP CLI, local or Browser Use cloud | skip, same harness |
| deep-research | One paid DeepAPI call (`POST /v1/research/deep`, minimum `maxCostUsd` `"0.35"`) | skip, local literature research already exists |
| deep-scrape | JSON dossier on a person, company or topic via DeepAPI | skip, due-diligence tool, not neuro methods |
| deepapi | Paid router for search, scrape, mail, SEO, images, VM, cloud browser; only domain-adjacent hook is arXiv (`references/scraping.md:17`) | skip, no NWB access and no loop |
| domain-checker | RDAP status of a domain | skip, no science relevance |
| fireflies-transcript | Read-only Fireflies meeting transcripts | skip |
| online-shopping | Price and shop-trust lookups via DeepAPI | skip |
| varied-search | Five web, GitHub and X searches each via DeepAPI | skip, thin wrapper on `deepapi` |
| who-is-this | Public person profile via DeepAPI | skip, person OSINT |

## The two gaps

The two things the team actually needs, a research loop (PROBLEM.md, answer key, referee, READ → PREDICT → RUN → JUDGE → RECORD) and NWB/DANDI access, exist nowhere in the repo.
Evidence: `gh-axi search code 'NWB OR DANDI OR pynwb OR neurodata OR "research loop" OR referee' --repo davidondrej/skills` returned `count: 0`, and a full-text pass over all 52 `SKILL.md` files found no hit on `nwb`, `dandi`, `pynwb`, `neurodata`, `dandiarchive`, `referee`, `answer key`, `research loop` or `PROBLEM.md`.
Read and discarded as not filling either gap: `goal-loop`, `signal-from-expert`, `risky-changes`, `teach`, `keep-track`, `decisions`, `adr-verbatim`.

The worthwhile work is to write those two skills ourselves, not to pull in a DeepAPI or browser skill.
