"""Tests for :mod:`agent_guard_eval.models`."""

from __future__ import annotations

from agent_guard_eval.models import (
    DiffDetail,
    GuardViolation,
    NumericMatch,
    ValidationResult,
    ViolationType,
)


def test_numeric_match_span_and_to_dict() -> None:
    match = NumericMatch(key="Sharpe", value=1.5, raw="1.5", start=8, end=11, source="number")
    assert match.span() == (8, 11)
    data = match.to_dict()
    assert data["key"] == "Sharpe"
    assert data["value"] == 1.5
    assert data["source"] == "number"


def test_numeric_match_defaults() -> None:
    match = NumericMatch(key="", value=0.0, raw="0", start=0, end=1, source="number")
    assert match.unit == ""
    assert match.to_dict()["unit"] == ""


def test_guard_violation_to_dict() -> None:
    violation = GuardViolation(
        violation_type=ViolationType.MISSING, key="Variance", message="missing"
    )
    data = violation.to_dict()
    assert data["violation_type"] == "missing"
    assert data["key"] == "Variance"
    assert data["expected"] is None


def test_validation_result_defaults_and_count() -> None:
    result = ValidationResult(is_valid=True)
    assert result.violation_count == 0
    assert result.violations == ()

    violation = GuardViolation(violation_type=ViolationType.MISMATCH, key="x", message="mismatch")
    result = ValidationResult(is_valid=False, violations=(violation,))
    assert result.violation_count == 1
    assert result.to_dict()["is_valid"] is False


def test_diff_detail_to_dict() -> None:
    diff = DiffDetail(
        key="x",
        expected=1.0,
        actual=2.0,
        raw_actual="2",
        absolute_error=1.0,
        relative_error=1.0,
        allowed_tolerance=0.001,
        passed=False,
    )
    data = diff.to_dict()
    assert data["passed"] is False
    assert data["relative_error"] == 1.0


def test_violation_type_values() -> None:
    assert ViolationType.MISMATCH.value == "mismatch"
    assert ViolationType.MISSING.value == "missing"
    assert ViolationType.UNEXPECTED.value == "unexpected"
    assert ViolationType.EXTRACTION_ERROR.value == "extraction_error"
