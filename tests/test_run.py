"""T8 (partial): run.py runs every implemented method on both splits and writes reproducible JSON.

Runs on a small synthetic .mat with the real layout, never on the real data.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from test_loader import _fake_raw, _write_mat

_spec = importlib.util.spec_from_file_location("run", Path(__file__).resolve().parents[1] / "run.py")
run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run)


def test_run_writes_one_result_per_split_and_method_reproducibly(tmp_path):
    p = tmp_path / "sleep_data.mat"
    _write_mat(p, _fake_raw(n_cells=30))
    argv = ["--data", str(p), "--seed", "0", "--n-shuffles", "20", "--no-cache"]
    assert run.main(argv + ["--out", str(tmp_path / "r1")]) == 0
    assert run.main(argv + ["--out", str(tmp_path / "r2")]) == 0

    methods = run.implemented_methods()
    assert {"M3", "M4"} <= set(methods)
    files = sorted(f.name for f in (tmp_path / "r1" / "real").glob("*.json"))
    assert files == sorted(f"mouse05_split{s}__{m}.json" for s in "AB" for m in methods)
    for name in files + ["summary.csv"]:
        assert (tmp_path / "r1" / "real" / name).read_bytes() == (tmp_path / "r2" / "real" / name).read_bytes()
    res = json.loads((tmp_path / "r1" / "real" / "mouse05_splitA__M3.json").read_text())
    assert res["session_id"] == "mouse05_splitA" and res["seed"] == 0


def test_run_missing_field_exits_nonzero(tmp_path, capsys):
    p = tmp_path / "sleep_data.mat"
    _write_mat(p, _fake_raw(), drop="spike")
    assert run.main(["--data", str(p), "--no-cache", "--out", str(tmp_path)]) == 1
    assert "required field 'spike' is missing" in capsys.readouterr().err
