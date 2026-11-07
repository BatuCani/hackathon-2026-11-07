"""One-command reproduction of every result (task T8 in TASKS.md).

Usage, from a fresh clone:

    uv run python run.py --data /path/to/sleep_data.mat --seed 0

Loads Split A and Split B (PROBLEM.md) with ``toolbox.loader``, runs every
implemented method (a module among M1-M4 that exposes ``run``) with N1, and writes
one ``MethodResult`` JSON per split and method plus ``summary.csv`` to
``<out>/real/``. Methods not implemented yet are listed as skipped.
Output holds no timestamps or paths, so equal inputs give byte-identical files.
Not yet wired: the method tests and the verdict rule (T7).
"""

from __future__ import annotations

import argparse
import csv
import importlib
import inspect
import math
import sys
from pathlib import Path

METHODS = {"M1": "toolbox.m1_pair_corr", "M2": "toolbox.m2_ev_rev", "M3": "toolbox.m3_pca", "M4": "toolbox.m4_ica"}


def implemented_methods() -> dict:
    """Method id -> module, for every method module that exposes ``run``."""
    out = {}
    for mid, name in METHODS.items():
        mod = importlib.import_module(name)
        if callable(getattr(mod, "run", None)):
            out[mid] = mod
    return out


def _call(mod, rec, seed: int, n_shuffles: int):
    params = None
    if "params" in inspect.signature(mod.run).parameters:
        from toolbox.assemblies import AssemblyParams

        if mod.__name__ in ("toolbox.m3_pca", "toolbox.m4_ica"):
            params = AssemblyParams(n_shuffles=n_shuffles)
    return mod.run(rec, seed=seed, params=params) if params is not None else mod.run(rec, seed=seed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, required=True, help="path to RIKEN sleep_data.mat (or its cached .npz)")
    parser.add_argument("--seed", type=int, default=0, help="master seed (default 0)")
    parser.add_argument("--out", type=Path, default=Path("results"), help="output directory (writes <out>/real/)")
    parser.add_argument("--n-cells", type=int, default=300, help="most active cells over both TASK windows, same in both splits (default 300; 0 = all)")
    parser.add_argument("--n-shuffles", type=int, default=500, help="N1 shuffles for M3/M4 (default 500, the answer key)")
    parser.add_argument("--no-cache", action="store_true", help="do not read or write the .npz cache")
    args = parser.parse_args(argv)

    from toolbox import loader

    try:
        kwargs = {"n_cells": args.n_cells or None}
        if args.no_cache:
            kwargs["cache_dir"] = None
        sessions = loader.load_sessions(args.data, **kwargs)
    except loader.LoaderError as e:
        print(f"run.py: {e}", file=sys.stderr)
        return 1

    methods = implemented_methods()
    skipped = sorted(set(METHODS) - set(methods))
    out = args.out / "real"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for rec in sessions:
        for mid, mod in methods.items():
            res = _call(mod, rec, args.seed, args.n_shuffles)
            (out / f"{rec.session_id}__{mid}.json").write_text(res.to_json() + "\n")
            rows.append({
                "session_id": rec.session_id, "method_id": mid, "n_cells": rec.deconv.shape[0],
                "eligible": res.eligible, "score": res.score, "p_n1": res.p_n1,
                "n_shuffles": res.n_shuffles, "seed": res.seed, "reason": res.reason,
            })
            score = "nan" if math.isnan(res.score) else f"{res.score:.6g}"
            p = "nan" if math.isnan(res.p_n1) else f"{res.p_n1:.4g}"
            print(f"{rec.session_id} {mid}: eligible={res.eligible} score={score} p_n1={p} {res.reason}")
    for mid in skipped:
        print(f"{mid}: skipped, not implemented ({METHODS[mid]} has no run())")

    with open(out / "summary.csv", "w", newline="") as f:
        fields = ["session_id", "method_id", "n_cells", "eligible", "score", "p_n1", "n_shuffles", "seed", "reason"]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        for mid in skipped:
            for rec in sessions:
                w.writerow({"session_id": rec.session_id, "method_id": mid, "eligible": False,
                            "reason": "not implemented", "seed": args.seed})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
