"""Helpers for building structured violations from comparison diffs."""

from __future__ import annotations

from ..models import DiffDetail, GuardViolation, NumericMatch, ViolationType


def build_mismatch_violation(diff: DiffDetail) -> GuardViolation:
    """Build a ``MISMATCH`` violation from a failed diff."""
    return GuardViolation(
        violation_type=ViolationType.MISMATCH,
        key=diff.key,
        message=(
            f"'{diff.key}' mismatch: expected {diff.expected}, got {diff.actual} "
            f"(raw '{diff.raw_actual}'); absolute error {diff.absolute_error}, "
            f"allowed tolerance {diff.allowed_tolerance}"
        ),
        expected=diff.expected,
        actual=diff.actual,
        raw_actual=diff.raw_actual,
        absolute_error=diff.absolute_error,
        relative_error=diff.relative_error,
        allowed_tolerance=diff.allowed_tolerance,
        unit=diff.unit,
    )


def build_missing_violation(key: str, expected: float, unit: str = "") -> GuardViolation:
    """Build a ``MISSING`` violation for a reference key absent from the text."""
    return GuardViolation(
        violation_type=ViolationType.MISSING,
        key=key,
        message=f"'{key}' was not found in the text (expected {expected})",
        expected=expected,
        unit=unit,
    )


def build_unexpected_violation(match: NumericMatch) -> GuardViolation:
    """Build an ``UNEXPECTED`` violation for a value with no reference counterpart."""
    return GuardViolation(
        violation_type=ViolationType.UNEXPECTED,
        key=match.key or match.raw,
        message=f"Unexpected numeric value '{match.raw}' has no reference counterpart",
        actual=match.value,
        raw_actual=match.raw,
        unit=match.unit,
    )
