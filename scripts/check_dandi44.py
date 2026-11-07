"""Load DANDI:000044 sessions and print frame counts per epoch and stage (no method is run).

    uv run --python 3.12 --with remfile python scripts/check_dandi44.py [session substring ...]
"""

import sys

import numpy as np

from toolbox.contract import analysis_mask
from toolbox.loader_dandi import dandi_urls, load_dandi44

for path, url in sorted(dandi_urls().items()):
    if len(sys.argv) > 1 and not any(s in path for s in sys.argv[1:]):
        continue
    rec = load_dandi44(url)
    n = rec.deconv.shape[0]
    m = {ep: int(analysis_mask(rec, ep).sum()) for ep in ("PRE", "TASK", "POST")}
    stages = {ep: {s: int(np.sum((rec.epoch == ep) & (rec.sleep_stage == s))) for s in ("wake", "NREM", "REM", "unscored")}
              for ep in ("PRE", "TASK", "POST")}
    print(f"{rec.session_id}: {n} pyramidal units, fs {rec.fs} Hz, spikes {int(rec.deconv.sum())}")
    print(f"  analysis frames {m}; TASK >= 5N: {m['TASK'] >= 5 * n} ({m['TASK']} vs {5 * n})")
    print(f"  stages per epoch {stages}")
