"""Write M1 results. Real splits when toolbox.loader.load_sessions exists, otherwise synthetic controls.

    uv run --python 3.12 python scripts/run_m1.py --seed 0

Synthetic files land in results/synthetic/M1_*.json.
Real files land in results/real/M1_<session_id>.json.
The script generates those files; do not edit them by hand.
"""

from __future__ import annotations

import argparse
import importlib
from dataclasses import replace
from pathlib import Path

import numpy as np

from toolbox.contract import analysis_mask
from toolbox.controls import scenario
from toolbox.m1_pair_corr import M1Params, run

ROOT = Path(__file__).resolve().parents[1]


def _loader_sessions():
    try:
        loader = importlib.import_module("toolbox.loader")
    except ImportError:
        return None, "toolbox.loader failed to import"
    load_sessions = getattr(loader, "load_sessions", None)
    if load_sessions is None:
        return None, "toolbox.loader has no load_sessions (stub)"
    try:
        sessions = list(load_sessions())
    except Exception as exc:
        return None, f"load_sessions failed: {exc}"
    if not sessions:
        return None, "load_sessions returned no sessions"
    return sessions, "real"


def _rate_confound(seed: int):
    rec = scenario("no_sleep_coactivity", seed=seed, tau_s=1.0)
    rng = np.random.default_rng(seed + 17)
    X = np.array(rec.deconv, dtype=np.float64, copy=True)
    mask = analysis_mask(rec, "POST")
    n = int(mask.sum())
    X[:, mask] += (rng.random((X.shape[0], n)) < 0.2) * rng.lognormal(0.0, 0.5, (X.shape[0], n))
    X[:, mask] *= np.linspace(3.0, 9.0, X.shape[0])[:, None]
    return replace(rec, deconv=X, session_id=f"rate-confound-{seed}")


def _synthetic(seed: int):
    return {
        "positive": scenario("positive", seed=seed, tau_s=1.0),
        "noise": scenario("noise_only", seed=seed, tau_s=1.0),
        "pre_existing": scenario("pre_existing", seed=seed, tau_s=1.0),
        "rate_confound": _rate_confound(seed),
    }


def _write(path: Path, result) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.to_json() + "\n")
    score = "nan" if result.score != result.score else f"{result.score:.4g}"
    p = "nan" if result.p_n1 != result.p_n1 else f"{result.p_n1:.4g}"
    print(f"{path.name}: eligible={result.eligible} score={score} p_n1={p} {result.reason}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-shuffles", type=int, default=500)
    args = ap.parse_args()
    params = M1Params(n_shuffles=args.n_shuffles)

    sessions, status = _loader_sessions()
    print(f"loader: {status}")
    if sessions is not None:
        for rec in sessions:
            name = {"mouse05_splitA": "M1_splitA", "mouse05_splitB": "M1_splitB"}.get(
                rec.session_id, f"M1_{rec.session_id}"
            )
            result = run(rec, seed=args.seed, params=params)
            _write(ROOT / "results" / "real" / f"{name}.json", result)
        return

    for name, rec in _synthetic(args.seed).items():
        result = run(rec, seed=args.seed, params=params)
        _write(ROOT / "results" / "synthetic" / f"M1_{name}.json", result)


if __name__ == "__main__":
    main()
