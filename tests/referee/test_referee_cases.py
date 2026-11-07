"""The cases carry the planted truth they claim, independent of any method."""

from __future__ import annotations

import numpy as np
import pytest

from referee import rules

cases = pytest.importorskip("referee.cases", reason="needs toolbox.synth (Engineer B, eng-b/toolbox)")
from toolbox.contract import analysis_mask


def _members_coactivity(rec, epoch: str) -> float:
    """Mean pairwise Pearson r among members of the same assembly, on the analysed frames."""
    X = rec.deconv[:, analysis_mask(rec, epoch)]
    rs = []
    for m in cases.members():
        C = np.corrcoef(X[m])
        rs.append(C[np.triu_indices(m.size, 1)].mean())
    return float(np.mean(rs))


def _members_rate(rec, epoch: str) -> float:
    X = rec.deconv[np.concatenate(cases.members())][:, analysis_mask(rec, epoch)]
    return float(X.mean())


@pytest.mark.parametrize("case", cases.CASES)
def test_shape_and_labels(case):
    rec = cases.make_case(case, rules.SEEDS[0])
    n_frames = sum(cases.FRAMES.values())
    assert rec.deconv.shape == (cases.N_CELLS, n_frames)
    assert rec.deconv.dtype == np.float64 and np.all(rec.deconv >= 0) and np.isfinite(rec.deconv).all()
    assert rec.fs == 7.65
    for ep in ("PRE", "POST"):
        nrem = int(analysis_mask(rec, ep).sum())
        assert nrem == round(cases.NREM_FRACTION * cases.FRAMES[ep]) and nrem >= 300
    assert set(rec.sleep_stage[rec.epoch == "TASK"]) == {"wake"}


@pytest.mark.parametrize("case", cases.CASES)
def test_deterministic(case):
    a, b = cases.make_case(case, rules.SEEDS[0]), cases.make_case(case, rules.SEEDS[0])
    assert a.deconv.tobytes() == b.deconv.tobytes()
    assert cases.make_case(case, rules.SEEDS[1]).deconv.tobytes() != a.deconv.tobytes()


def test_planted_truth():
    """Medians over the referee seeds; the numbers are loose on purpose."""
    def med(case, f, epoch):
        return float(np.median([f(cases.make_case(case, s), epoch) for s in rules.SEEDS]))

    # a: co-active in TASK and POST, not PRE.
    assert med("a_reactivation", _members_coactivity, "TASK") > 0.1
    assert med("a_reactivation", _members_coactivity, "POST") > 0.07
    assert abs(med("a_reactivation", _members_coactivity, "PRE")) < 0.03
    # b: nothing co-active anywhere.
    for ep in ("PRE", "TASK", "POST"):
        assert abs(med("b_noise", _members_coactivity, ep)) < 0.03
    # c: PRE and POST equally co-active.
    pre, post = med("c_preexisting", _members_coactivity, "PRE"), med("c_preexisting", _members_coactivity, "POST")
    assert pre > 0.07 and abs(post - pre) < 0.05
    # d: members fire more in POST, but are not co-active there.
    ratio = np.median(
        [_members_rate(r, "POST") / _members_rate(r, "PRE")
         for r in (cases.make_case("d_rate_only", s) for s in rules.SEEDS)]
    )
    assert 1.5 < ratio < 3.5
    assert med("d_rate_only", _members_coactivity, "TASK") > 0.1
    assert abs(med("d_rate_only", _members_coactivity, "POST")) < 0.03
    assert abs(med("d_rate_only", _members_coactivity, "PRE")) < 0.03
