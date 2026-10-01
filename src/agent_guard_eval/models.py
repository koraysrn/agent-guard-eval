"""Data models used throughout the validation pipeline.

All models are frozen dataclasses; validation results are therefore immutable and
safe to share across threads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ViolationType(str, Enum):
    """Kinds of violations that the guard can report."""

    MISMATCH = "mismatch"
    """A key matched, but its value drifted outside the allowed tolerance."""

    MISSING = "missing"
    """A reference key could not be found anywhere in the text."""

    UNEXPECTED = "unexpected"
    """An extra numeric value with no reference counterpart was found."""

    EXTRACTION_ERROR = "extraction_error"
    """An error occurred while extracting numeric values."""


@dataclass(frozen=True, slots=True)
class NumericMatch:
    """A single numeric value extracted from the input text."""

    key: str
    value: float
    raw: str
    start: int
    end: int
    source: str
    unit: str = ""

    def span(self) -> tuple[int, int]:
        """Return the ``(start, end)`` character range of the match in the text."""
        return (self.start, self.end)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "raw": self.raw,
            "start": self.start,
            "end": self.end,
            "source": self.source,
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class DiffDetail:
    """Difference detail between a reference value and a text value for one key."""

    key: str
    expected: float
    actual: float
    raw_actual: str
    absolute_error: float
    relative_error: float | None
    allowed_tolerance: float
    passed: bool
    unit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "expected": self.expected,
            "actual": self.actual,
            "raw_actual": self.raw_actual,
            "absolute_error": self.absolute_error,
            "relative_error": self.relative_error,
            "allowed_tolerance": self.allowed_tolerance,
            "passed": self.passed,
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class GuardViolation:
    """A structured violation record."""

    violation_type: ViolationType
    key: str
    message: str
    expected: float | None = None
    actual: float | None = None
    raw_actual: str | None = None
    absolute_error: float | None = None
    relative_error: float | None = None
    allowed_tolerance: float | None = None
    unit: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_type": self.violation_type.value,
            "key": self.key,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
            "raw_actual": self.raw_actual,
            "absolute_error": self.absolute_error,
            "relative_error": self.relative_error,
            "allowed_tolerance": self.allowed_tolerance,
            "unit": self.unit,
        }


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Final result of a validation run."""

    is_valid: bool
    violations: tuple[GuardViolation, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)
    text_length: int = 0
    extracted_count: int = 0

    @property
    def violation_count(self) -> int:
        """Total number of violations."""
        return len(self.violations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "violation_count": self.violation_count,
            "violations": [v.to_dict() for v in self.violations],
            "details": self.details,
            "text_length": self.text_length,
            "extracted_count": self.extracted_count,
        }
