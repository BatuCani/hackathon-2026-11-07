# Hackathon build approach

## The minimum viable scientific loop

`input validation -> movement-only encoding -> candidate bursts -> decode -> score -> shuffle test -> auditable report`

### 1. Agree the scientific contract (first 20–30 minutes)

- Name the input columns and units: `time`, `position`, `speed` (if present), `neuron_id`, spike time, and optional LFP.
- Decide whether the environment is a linear track, a maze that can be linearised, or a synthetic demo. The first MVP assumes a 1-D track.
- Write a one-sentence success condition: “On held-out running data the decoder localises position above a stated baseline, and injected sequences are recovered with an empirically measured false-positive rate.”
- Assign the domain scientist ownership of thresholds and what counts as a useful event; assign the builder ownership of reproducibility and tests.

### 2. Build the vertical slice first (about 90 minutes)

Create a Python notebook or CLI with no UI:

1. Load a tiny, versioned CSV/NPZ fixture.
2. Split running data from immobility data using an explicit speed criterion.
3. Fit smoothed place-rate maps from running data only.
4. Decode an example event into a time × position posterior using a Poisson naïve Bayes model.
5. Render one raster, one posterior heat map, and its best-path / weighted-correlation score.
6. Save all parameters plus a seed beside the result.

Before working on real data, generate synthetic place cells and inject a known forward/reverse sequence. This makes it possible to test the decoder rather than merely produce a plot.

### 3. Add honest event calls (next 90 minutes)

- Detect candidate population bursts; if LFP exists, report ripple-band power as a second observable rather than silently hard-coding it.
- Require a documented minimum duration and number of active units.
- Score with one primary method (weighted correlation or linear-fit mass) and retain the rank-order score as a secondary diagnostic.
- Run at least 1,000 seeded shuffles when time permits; otherwise mark lower counts as exploratory.
- Call an event only if it passes every predeclared null test, and display the observed score, null distribution, percentile/p-value, and pass/fail reason.

### 4. Validate before polishing (final 60–90 minutes)

Use three tests:

| Test | Expected outcome |
| --- | --- |
| Held-out running position | Decoder beats a simple occupancy/constant-position baseline. |
| Injected forward/reverse synthetic replay | Known event is recovered with direction and approximate trajectory. |
| Shuffled or cell-ID-randomised data | Event calls fall to the declared empirical false-positive range. |

If the data include two tracks, implement Takigawa et al.’s independent sequenceless log-odds check. If not, do not pretend a single-track dataset has that validation; use injected-positive and shuffled-negative controls.

## Suggested repository shape

```text
src/
  io.py                 # schema checks and units
  simulation.py         # deterministic fixture and injected replay
  place_fields.py       # movement-only rate maps
  candidates.py         # burst / optional ripple candidates
  decode.py             # posterior computation
  score.py              # weighted correlation / line score
  nulls.py              # predeclared shuffle functions
  report.py             # figures + JSON provenance
tests/
  test_synthetic_replay.py
  test_null_controls.py
config/example.yaml
```

## Division of labour

- **Scientist:** describes behavioural epochs, units, valid neurons, and plausible event criteria; inspects edge cases.
- **Engineer:** makes the pipeline deterministic, data-validated, and runnable in one command.
- **Both:** preregister the demo parameters in `config/example.yaml` before viewing candidate-event results.

## Demo narrative

Show one real/synthetic event end-to-end: raw spike raster → posterior trajectory → observed score versus shuffles → decision and uncertainty. Then show the negative control. This makes the result useful even if the team does not reach a production classifier.

