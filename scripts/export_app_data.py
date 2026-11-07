"""Export small JSON files the web app animates (app/derived/).

Command, from the repository root:

    OMP_NUM_THREADS=1 uv run --python 3.12 --with matplotlib python scripts/export_app_data.py

It reuses the helpers in scripts/plot_method_panels.py with 500 N1 shuffles and seed 0, the settings of
results/real/, and checks that each recomputed p matches the run p before writing anything.

- app/derived/buddy_reactivation.json: PCA reactivation strength R(t) for DANDI:000044 Buddy_06272013, mean of
  the significant templates, in equal bins per epoch (PRE and POST are NREM frames only). Display only; the
  score is POST mean minus PRE mean on the unbinned trace.
- app/derived/null_distributions.json: the 500 shuffled-control scores for M1, M3 and M4 on Buddy_06272013, with
  the real score and p. Each recomputed p matches results/real/dandi/summary.csv. RIKEN split A is not exported:
  the panels loader path gives slightly different scores from results/real/, so the app derives RIKEN from p.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("panels", ROOT / "scripts" / "plot_method_panels.py")
panels = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panels)

from toolbox.assemblies import AssemblyParams, reactivation_strength, zscore  # noqa: E402
from toolbox.loader_dandi import load_dandi44  # noqa: E402
from toolbox.m1_pair_corr import M1Params, _prepare, run as run_m1  # noqa: E402
from toolbox.m3_pca import run_with_traces as run_m3  # noqa: E402
from toolbox.m4_ica import run_with_traces as run_m4  # noqa: E402
from toolbox.nulls import n1_pvalue  # noqa: E402

N = 500
SEED = 0
BINS = 60
OUT = ROOT / "app" / "derived"


def _bins(x: np.ndarray, n: int) -> list[float]:
    edges = np.linspace(0, x.size, n + 1).astype(int)
    return [round(float(x[a:max(b, a + 1)].mean()), 4) for a, b in zip(edges[:-1], edges[1:])]


def _assembly(rec, runner, label: str) -> tuple[dict, dict | None]:
    result, traces = runner(rec, seed=SEED, params=AssemblyParams(n_shuffles=N))
    W = np.asarray(result.details["weights"], dtype=np.float64)
    kept = panels._kept_index(rec, result.details["kept_cell_ids"])
    null = panels._strength_null(rec, W, kept, N)
    p = n1_pvalue(float(result.score), null)
    if abs(p - float(result.p_n1)) > 1e-9:
        raise RuntimeError(f"{label} {rec.session_id}: null p {p} != run p {result.p_n1}")
    block = {"score": float(result.score), "p": float(result.p_n1), "null": [round(float(v), 5) for v in null]}
    return block, (result, traces, W, kept)


def _session(rec, with_trace: bool) -> tuple[dict, dict | None]:
    m1 = run_m1(rec, seed=SEED, params=M1Params(n_shuffles=N))
    null_m1 = panels._m1_null(_prepare(rec, M1Params(n_shuffles=N)), N, rec.session_id)
    finite = null_m1[np.isfinite(null_m1)]
    p1 = n1_pvalue(float(m1.score), finite)
    if abs(p1 - float(m1.p_n1)) > 1e-9:
        raise RuntimeError(f"M1 {rec.session_id}: null p {p1} != run p {m1.p_n1}")
    out = {"M1": {"score": float(m1.score), "p": float(m1.p_n1), "null": [round(float(v), 5) for v in finite]}}
    out["M3"], m3 = _assembly(rec, run_m3, "M3")
    out["M4"], _ = _assembly(rec, run_m4, "M4")
    trace = None
    if with_trace:
        result, traces, W, kept = m3
        n_sig = int(result.details["n_sig"])
        r_task = reactivation_strength(W[:, :n_sig], zscore(panels._epoch(rec, "TASK")[kept]))
        mean = {
            "PRE": np.asarray(traces["R_pre"][:n_sig]).mean(axis=0),
            "TASK": np.asarray(r_task).mean(axis=0),
            "POST": np.asarray(traces["R_post"][:n_sig]).mean(axis=0),
        }
        trace = {
            "source": "scripts/export_app_data.py (toolbox M3, seed 0, 500 N1 shuffles)",
            "session": rec.session_id,
            "n_templates": n_sig,
            "bins_per_epoch": BINS,
            "frames": {k: int(v.size) for k, v in mean.items()},
            "epoch_mean": {k: round(float(v.mean()), 4) for k, v in mean.items()},
            "score": float(result.score),
            "p": float(result.p_n1),
            "R": {k: _bins(v, BINS) for k, v in mean.items()},
        }
    return out, trace


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    yes_path = Path("/Users/batu/hackathon-data/000044/sub-Buddy_ses-Buddy-06272013_behavior+ecephys.nwb")
    panels._log(f"load {yes_path.name}")
    yes = load_dandi44(yes_path)
    yes_nulls, trace = _session(yes, True)
    (OUT / "buddy_reactivation.json").write_text(json.dumps(trace, separators=(",", ":")) + "\n")
    meta = {"source": "scripts/export_app_data.py (toolbox, seed 0, 500 N1 shuffles)", "n_shuffles": N}
    nulls = {**meta, "yes": {"session": yes.session_id, **yes_nulls}}
    (OUT / "null_distributions.json").write_text(json.dumps(nulls, separators=(",", ":")) + "\n")
    panels._log(f"wrote {OUT}")


if __name__ == "__main__":
    main()
