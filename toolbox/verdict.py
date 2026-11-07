"""Verdict rule (DRAFT pending Zixi).

Turns MethodResults and control outcomes into the overall verdict defined in
PROBLEM.md: reactivation likely, not supported, or not enough evidence.

Per PROBLEM.md (Overall verdict, DRAFT, owner Zixi):
- Counted methods = eligible methods that passed their method tests.
- Reactivation likely: at least two counted methods say "yes" in both splits,
  and no counted method says "yes" in the reversed direction (POST and PRE swapped).
- Reactivation not supported: no counted method says "yes" in either split.
- Not enough evidence: anything else, including fewer than two counted methods.

The report also states the fraction of counted methods saying "yes" per split,
as the "how likely" number (unit: methods / counted methods).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

from .contract import MethodResult
from .controls import ControlReport

VerdictCategory = Literal[
    "Reactivation likely",
    "Reactivation not supported",
    "Not enough evidence",
]


def method_says_yes(result: MethodResult, alpha: float = 0.05) -> bool:
    """Return True if a method result satisfies the answer-key 'yes' threshold.

    Score must be strictly positive and p_n1 must be strictly less than alpha.
    Ineligible runs or NaN scores/p-values return False.
    """
    if not result.eligible:
        return False
    if math.isnan(result.score) or result.score <= 0:
        return False
    if result.p_n1 is None or math.isnan(result.p_n1) or result.p_n1 >= alpha:
        return False
    return True


def method_passed_controls(
    method_id: str,
    controls: Mapping[str, bool | ControlReport] | None,
) -> bool:
    """Check if a method passed its synthetic positive and negative controls.

    If controls is None, methods are considered passed by default.
    If controls mapping is provided, the method must be present and report passed=True.
    """
    if controls is None:
        return True
    ctrl = controls.get(method_id)
    if ctrl is None:
        return False
    if isinstance(ctrl, ControlReport):
        return bool(ctrl.passed)
    return bool(ctrl)


@dataclass(frozen=True)
class VerdictResult:
    """Result of evaluating the overall reactivation verdict."""

    verdict: VerdictCategory
    how_likely: dict[str, float]
    how_likely_str: dict[str, str]
    counted_methods: list[str]
    counted_per_split: dict[str, list[str]]
    yes_per_split: dict[str, list[str]]
    yes_both_splits: list[str]
    ineligible_methods: dict[str, list[str]]
    failed_control_methods: list[str]
    reversed_yes_methods: list[str]
    details: dict[str, Any] = field(default_factory=dict)


def _normalize_results(
    results: Iterable[MethodResult]
    | Mapping[tuple[str, str], MethodResult]
    | Mapping[str, Iterable[MethodResult]],
) -> dict[tuple[str, str], MethodResult]:
    """Normalize input results into a dict keyed by (method_id, session_id)."""
    norm: dict[tuple[str, str], MethodResult] = {}
    if isinstance(results, Mapping):
        for k, v in results.items():
            if isinstance(k, tuple) and len(k) == 2 and isinstance(v, MethodResult):
                norm[(v.method_id, v.session_id)] = v
            elif isinstance(k, str) and isinstance(v, MethodResult):
                norm[(v.method_id, v.session_id)] = v
            elif isinstance(v, Iterable):
                for item in v:
                    if isinstance(item, MethodResult):
                        norm[(item.method_id, item.session_id)] = item
    elif isinstance(results, Iterable):
        for item in results:
            if isinstance(item, MethodResult):
                norm[(item.method_id, item.session_id)] = item
    return norm


def compute_verdict(
    results: Iterable[MethodResult]
    | Mapping[tuple[str, str], MethodResult]
    | Mapping[str, Iterable[MethodResult]],
    controls: Mapping[str, bool | ControlReport] | None = None,
    reversed_results: Iterable[MethodResult]
    | Mapping[tuple[str, str], MethodResult]
    | None = None,
    splits: Sequence[str] | None = None,
    alpha: float = 0.05,
) -> VerdictResult:
    """Compute the overall reactivation verdict from method results and controls.

    Parameters
    ----------
    results:
        Forward method results across splits/sessions.
    controls:
        Outcomes of positive and negative control tests per method.
    reversed_results:
        Optional method results obtained with PRE and POST swapped.
    splits:
        Specific split IDs to evaluate (default: all split IDs found in results).
    alpha:
        Significance threshold for p_n1 (default: 0.05).
    """
    norm_res = _normalize_results(results)

    # Determine splits
    if splits is None:
        seen_splits: list[str] = []
        for _, sid in norm_res:
            if sid not in seen_splits:
                seen_splits.append(sid)
        eval_splits = seen_splits
    else:
        eval_splits = list(splits)

    # Determine all methods observed
    seen_methods: list[str] = []
    for mid, _ in norm_res:
        if mid not in seen_methods:
            seen_methods.append(mid)

    # Check controls per method
    failed_controls: list[str] = []
    for mid in seen_methods:
        if not method_passed_controls(mid, controls):
            failed_controls.append(mid)

    # Check eligibility per method and split
    ineligible_info: dict[str, list[str]] = {}
    for mid in seen_methods:
        reasons: list[str] = []
        for sid in eval_splits:
            r = norm_res.get((mid, sid))
            if r is not None and not r.eligible:
                msg = f"{sid}: {r.reason}"
                if r.missing:
                    msg += f" (missing: {', '.join(r.missing)})"
                reasons.append(msg)
        if reasons:
            ineligible_info[mid] = reasons

    # Counted methods per split
    counted_per_split: dict[str, list[str]] = {}
    yes_per_split: dict[str, list[str]] = {}
    how_likely: dict[str, float] = {}
    how_likely_str: dict[str, str] = {}

    for sid in eval_splits:
        counted_in_sid: list[str] = []
        yes_in_sid: list[str] = []
        for mid in seen_methods:
            r = norm_res.get((mid, sid))
            if r is None:
                continue
            # Method must be eligible and pass controls to be counted
            if r.eligible and mid not in failed_controls:
                counted_in_sid.append(mid)
                if method_says_yes(r, alpha=alpha):
                    yes_in_sid.append(mid)
        counted_per_split[sid] = counted_in_sid
        yes_per_split[sid] = yes_in_sid
        n_yes = len(yes_in_sid)
        n_cnt = len(counted_in_sid)
        how_likely[sid] = (n_yes / n_cnt) if n_cnt > 0 else 0.0
        how_likely_str[sid] = f"{n_yes}/{n_cnt}"

    # Overall counted methods: eligible in all evaluated splits and passed controls
    overall_counted: list[str] = []
    for mid in seen_methods:
        if mid in failed_controls:
            continue
        eligible_all = all(
            (mid, sid) in norm_res and norm_res[(mid, sid)].eligible
            for sid in eval_splits
        )
        if eligible_all:
            overall_counted.append(mid)

    # Counted methods that say yes in all evaluated splits
    yes_both_splits = [
        mid for mid in overall_counted
        if all(mid in yes_per_split[sid] for sid in eval_splits)
    ]

    # Reversed direction check
    norm_rev = _normalize_results(reversed_results) if reversed_results else {}
    reversed_yes: list[str] = []
    for mid in overall_counted:
        # Check explicit reversed results
        for (rev_mid, _), rev_res in norm_rev.items():
            if rev_mid == mid and method_says_yes(rev_res, alpha=alpha):
                if mid not in reversed_yes:
                    reversed_yes.append(mid)
        # Also check details on forward results if stored there
        for sid in eval_splits:
            fwd_res = norm_res.get((mid, sid))
            if fwd_res is not None and fwd_res.details.get("reversed_says_yes") is True:
                if mid not in reversed_yes:
                    reversed_yes.append(mid)

    # Apply verdict logic
    if len(eval_splits) == 0 or len(overall_counted) < 2:
        verdict: VerdictCategory = "Not enough evidence"
    elif len(yes_both_splits) >= 2 and len(reversed_yes) == 0:
        verdict = "Reactivation likely"
    elif all(len(yes_per_split[sid]) == 0 for sid in eval_splits):
        verdict = "Reactivation not supported"
    else:
        verdict = "Not enough evidence"

    return VerdictResult(
        verdict=verdict,
        how_likely=how_likely,
        how_likely_str=how_likely_str,
        counted_methods=overall_counted,
        counted_per_split=counted_per_split,
        yes_per_split=yes_per_split,
        yes_both_splits=yes_both_splits,
        ineligible_methods=ineligible_info,
        failed_control_methods=failed_controls,
        reversed_yes_methods=reversed_yes,
        details={
            "splits": eval_splits,
            "all_methods": seen_methods,
            "alpha": alpha,
        },
    )


def generate_summary_markdown(
    verdict: VerdictResult,
    results: Iterable[MethodResult]
    | Mapping[tuple[str, str], MethodResult]
    | Mapping[str, Iterable[MethodResult]],
    controls: Mapping[str, bool | ControlReport] | None = None,
    reversed_results: Iterable[MethodResult]
    | Mapping[tuple[str, str], MethodResult]
    | None = None,
    out_path: Path | str | None = None,
) -> str:
    """Generate a clean markdown summary table for results/real/summary.md.

    If out_path is specified, writes the generated markdown to that file.
    Returns the markdown string.
    """
    norm_res = _normalize_results(results)
    splits = verdict.details.get("splits", list(verdict.how_likely.keys()))

    lines: list[str] = [
        "# Reactivation Analysis Summary",
        "",
        f"**Overall Verdict: {verdict.verdict}**",
        "",
        "## 1. Verdict Overview",
        "",
        f"- Overall verdict: **{verdict.verdict}**",
        f"- Counted methods: {', '.join(verdict.counted_methods) if verdict.counted_methods else 'None'}",
        "- How likely per split (fraction of counted methods saying yes):",
    ]

    for sid in splits:
        frac_str = verdict.how_likely_str.get(sid, "0/0")
        frac_val = verdict.how_likely.get(sid, 0.0)
        lines.append(f"  - {sid}: {frac_str} ({frac_val:.1%})")

    rev_note = "Passed (no counted method showed reverse reactivation)"
    if verdict.reversed_yes_methods:
        rev_note = f"Failed (reverse reactivation detected in: {', '.join(verdict.reversed_yes_methods)})"
    lines.extend([
        f"- Reversed direction check: {rev_note}",
        "",
        "## 2. Method Results Table",
        "",
        "| Method | Split | Eligible | Controls | Counted | Score | p_N1 | Yes? | Reason / Missing |",
        "|---|---|---|---|---|---|---|---|---|",
    ])

    sorted_keys = sorted(norm_res.keys())
    for mid, sid in sorted_keys:
        res = norm_res[(mid, sid)]
        ctrl_passed = method_passed_controls(mid, controls)
        counted = (mid in verdict.counted_per_split.get(sid, []))
        says_yes = method_says_yes(res)
        score_str = f"{res.score:.4f}" if not math.isnan(res.score) else "N/A"
        p_str = f"{res.p_n1:.4f}" if (res.p_n1 is not None and not math.isnan(res.p_n1)) else "N/A"
        reason = res.reason or ""
        if res.missing:
            reason += f" (missing: {', '.join(res.missing)})"

        lines.append(
            f"| {mid} | {sid} | {'Yes' if res.eligible else 'No'} | "
            f"{'Passed' if ctrl_passed else 'Failed'} | "
            f"{'Yes' if counted else 'No'} | {score_str} | {p_str} | "
            f"{'Yes' if says_yes else 'No'} | {reason} |"
        )

    lines.extend([
        "",
        "## 3. Ineligible Methods and Failed Controls",
        "",
    ])

    if verdict.ineligible_methods:
        lines.append("### Ineligible Methods")
        for mid, reasons in verdict.ineligible_methods.items():
            lines.append(f"- **{mid}**: {'; '.join(reasons)}")
        lines.append("")
    else:
        lines.append("No ineligible methods.")
        lines.append("")

    if verdict.failed_control_methods:
        lines.append("### Failed Method Tests (Controls)")
        for mid in verdict.failed_control_methods:
            lines.append(f"- **{mid}**: Failed synthetic control tests.")
        lines.append("")
    else:
        lines.append("All tested methods passed positive/negative controls.")
        lines.append("")

    content = "\n".join(lines) + "\n"

    if out_path is not None:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    return content
