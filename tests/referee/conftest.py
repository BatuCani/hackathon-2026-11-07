"""Referee harness: one core, importable as `referee`, and the 30 s budget."""

from __future__ import annotations

import os
import sys
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_var, "1")

_TESTS_DIR = str(Path(__file__).resolve().parent.parent)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

import pytest

from referee import rules

_HERE = Path(__file__).resolve().parent
_elapsed = {"total": 0.0}


def pytest_runtest_logreport(report):
    if Path(str(report.fspath)).resolve().parent == _HERE:
        _elapsed["total"] += report.duration


def pytest_terminal_summary(terminalreporter):
    total = _elapsed["total"]
    if total:
        terminalreporter.write_line(
            f"referee: {total:.1f} s of {rules.TIME_BUDGET_S:.0f} s budget"
        )


def pytest_sessionfinish(session, exitstatus):
    if _elapsed["total"] > rules.TIME_BUDGET_S and exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        print(
            f"\nreferee FAILED: took {_elapsed['total']:.1f} s, budget is "
            f"{rules.TIME_BUDGET_S:.0f} s on one core",
            file=sys.stderr,
        )
