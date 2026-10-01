"""Tests for :mod:`agent_guard_eval.report.diff`."""

from __future__ import annotations

from agent_guard_eval.models import DiffDetail, NumericMatch, ViolationType
from agent_guard_eval.report.diff import (
    build_mismatch_violation,
    build_missing_violation,
    build_unexpected_violation,
)


def test_mismatch_violation() -> None:
    diff = DiffDetail(
        key="Sharpe",
        expected=1.5,
        actual=1.9,
        raw_actual="1.9",
        absolute_error=0.4,
        relative_error=0.2666,
        allowed_tolerance=0.000151,
        passed=False,
    )
    violation = build_mismatch_violation(diff)
    assert violation.violation_type is ViolationType.MISMATCH
    assert violation.key == "Sharpe"
    assert violation.actual == 1.9
    assert "mismatch" in violation.message


def test_missing_violation() -> None:
    violation = build_missing_violation("Variance", 0.04, "%")
    assert violation.violation_type is ViolationType.MISSING
    assert violation.key == "Variance"
    assert violation.expected == 0.04
    assert violation.unit == "%"


def test_unexpected_violation() -> None:
    match = NumericMatch("", 3.14, "3.14", 0, 4, "number")
    violation = build_unexpected_violation(match)
    assert violation.violation_type is ViolationType.UNEXPECTED
    assert violation.actual == 3.14
    assert "3.14" in violation.message
