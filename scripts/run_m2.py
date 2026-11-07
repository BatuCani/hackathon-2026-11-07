"""Run M2 (EV / REV) and write results/<data>/M2_*.json.

Without --data: two synthetic pseudo-sessions (controls.scenario "positive", seeds 0 and 1) stand in
for splits A and B. With --data: real splits via
toolbox.loader into results/real/.
"""

import argparse
import json
import pathlib

from toolbox import m2_ev_rev as m2
from toolbox.controls import scenario

ap = argparse.ArgumentParser()
ap.add_argument("--data")
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--n-shuffles", type=int, default=500)
a = ap.parse_args()
params = m2.M2Params(n_shuffles=a.n_shuffles)
root = pathlib.Path(__file__).resolve().parents[1] / "results"
if a.data:
    from toolbox import loader

    out = root / "real"
    recs = dict(zip(("A", "B"), loader.load_sessions(a.data)))
    data_note = f"real: {a.data}, loader defaults (300 most active cells over both TASK bouts)"
else:
    out = root / "synthetic"
    recs = {"A": scenario("positive", seed=0, tau_s=1.0), "B": scenario("positive", seed=1, tau_s=1.0)}
    data_note = "synthetic: controls.scenario('positive', seed 0 / 1, tau_s 1.0) as pseudo-splits A / B"
out.mkdir(parents=True, exist_ok=True)
results = []
for split, rec in recs.items():
    r = m2.run(rec, seed=a.seed, params=params)
    results.append(r)
    (out / f"M2_split{split}.json").write_text(r.to_json() + "\n")
v = m2.verdict(results)
v["data"] = data_note
(out / "M2_verdict.json").write_text(json.dumps(v, sort_keys=True, indent=1) + "\n")
print(json.dumps(v, sort_keys=True, indent=1))
