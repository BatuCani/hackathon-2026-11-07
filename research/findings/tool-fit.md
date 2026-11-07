# Tool fit: open-source packages against the team brief

Fit of the packages from [oss-toolboxes.md](oss-toolboxes.md) against each part of the reactivation toolbox in [../team-brief.md](../team-brief.md).
As of 2026-11-07.

| Brief part | Open-source coverage | Who builds it |
|---|---|---|
| Loader (sleep stages, stim frames, PRE/TASK/POST) | `pynwb` / `dandi` read NWB from DANDI | Ours: the loader, the required-field check and the PRE/TASK/POST derivation |
| M1 cell-pair correlation | Plain numpy | Ours |
| M2 EV/REV | `neurospatial` (MIT, git pin `0cc33ecd`) has `explained_variance_reactivation` and `ev_rev_contrast` | Ours; neurospatial as an independent cross-check |
| M3/M4 PCA/ICA reactivation strength | `neurospatial` has `detect_assemblies` and `assembly_reactivation` | Ours; neurospatial as a cross-check. Unverified whether it accepts deconvolved calcium matrices rather than spike counts |
| N1 circular-shift null and the N1 eigenvalue bound | Not in any package | Ours |
| Requirement check and verdict rule | Not in any package | Ours; this is the core of the toolbox |
| neurospatial's replay part | Irrelevant: replay is out of scope | - |

## Recommendation

Implement M1-M4 from the equations, as the brief says.
Use `neurospatial` only as an independent reference implementation in the referee tests.
GPL code (`RnR_methods`, `NeuroPy`, `spykshrk`) stays reference-only.
