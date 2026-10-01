"""Comparator for plain numeric values."""

from __future__ import annotations

from ..config import GuardConfig
from ..models import DiffDetail, NumericMatch
from .base import allowed_tolerance, compute_errors, within_tolerance


class NumericComparator:
    """Compares a numeric match against a reference value using ``atol + rtol``."""

    def __init__(self, config: GuardConfig) -> None:
        self.config = config

    def compare(
        self,
        key: str,
        match: NumericMatch,
        expected: float,
        unit: str = "",
    ) -> DiffDetail:
        """Produce a :class:`DiffDetail` for the given key and match."""
        passed = within_tolerance(match.value, expected, self.config.atol, self.config.rtol)
        absolute_error, relative_error = compute_errors(match.value, expected)
        return DiffDetail(
            key=key,
            expected=expected,
            actual=match.value,
            raw_actual=match.raw,
            absolute_error=absolute_error,
            relative_error=relative_error,
            allowed_tolerance=allowed_tolerance(
                expected, self.config.atol, self.config.rtol
            ),
            passed=passed,
            unit=unit or match.unit,
        )
