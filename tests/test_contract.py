import json
import math

from toolbox.contract import MethodResult


def test_method_result_json_is_deterministic_and_nan_safe():
    result = MethodResult(
        method_id="M3",
        session_id="split-A",
        eligible=False,
        reason="0 TASK components above N1 bound",
        score=math.nan,
        p_n1=math.nan,
        n_shuffles=500,
        seed=0,
        params={"bound_quantile": 0.95},
        details={"n_sig": 0},
        missing=("TASK components above N1 bound >= 1",),
    )
    text = result.to_json()
    assert text == result.to_json()
    decoded = json.loads(text)
    assert decoded["score"] is None
    assert decoded["p_n1"] is None
    assert decoded["missing"] == ["TASK components above N1 bound >= 1"]
