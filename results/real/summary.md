# Reactivation Analysis Summary

**Overall Verdict: Not enough evidence**

## 1. Verdict Overview

- Overall verdict: **Not enough evidence**
- Counted methods: M1
- How likely per split (fraction of counted methods saying yes):
  - mouse05_splitA: 0/2 (0.0%)
  - mouse05_splitB: 0/1 (0.0%)
- Reversed direction check: Passed (no counted method showed reverse reactivation)

## 2. Method Results Table

| Method | Split | Eligible | Controls | Counted | Score | p_N1 | Yes? | Reason / Missing |
|---|---|---|---|---|---|---|---|---|
| M1 | mouse05_splitA | Yes | Passed | Yes | -0.0691 | 1.0000 | No |  |
| M1 | mouse05_splitB | Yes | Passed | Yes | 0.0061 | 0.1936 | No |  |
| M2 | mouse05_splitA | Yes | Failed | No | -0.0261 | 1.0000 | No |  |
| M2 | mouse05_splitB | Yes | Failed | No | 0.0017 | 0.0020 | Yes |  |
| M3 | mouse05_splitA | Yes | Passed | Yes | -0.1455 | 1.0000 | No |  |
| M3 | mouse05_splitB | No | Passed | No | N/A | N/A | No | TASK frames 651 < 1500 (5 per cell x 300 cells) (missing: TASK frames >= 1500) |
| M4 | mouse05_splitA | Yes | Failed | No | -0.0607 | 1.0000 | No |  |
| M4 | mouse05_splitB | No | Failed | No | N/A | N/A | No | TASK frames 651 < 1500 (5 per cell x 300 cells) (missing: TASK frames >= 1500) |

## 3. Ineligible Methods and Failed Controls

### Ineligible Methods
- **M3**: mouse05_splitB: TASK frames 651 < 1500 (5 per cell x 300 cells) (missing: TASK frames >= 1500)
- **M4**: mouse05_splitB: TASK frames 651 < 1500 (5 per cell x 300 cells) (missing: TASK frames >= 1500)

### Failed Method Tests (Controls)
- **M2**: Failed synthetic control tests.
- **M4**: Failed synthetic control tests.

