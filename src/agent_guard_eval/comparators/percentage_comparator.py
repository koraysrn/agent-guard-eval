"""Comparator for percentage values with basis-point awareness."""

from __future__ import annotations

from ..config import GuardConfig
from ..models import DiffDetail, NumericMatch
from .base import allowed_tolerance, compute_errors, within_tolerance


class PercentageComparator:
    """Compares percentage values, optionally interpreting references as fractions."""

    def __init__(self, config: GuardConfig) -> None:
        self.config = config

    def compare(
        self,
        key: str,
        match: NumericMatch,
        expected: float,
        unit: str = "%",
    ) -> DiffDetail:
        """Produce a :class:`DiffDetail` for the given percentage key and match."""
        actual = match.value
        # When references are fractions (0.15), convert "15%" style values to 0.15.
        if self.config.percent_as_fraction and match.unit == "%":
            actual = actual / 100.0

        passed = within_tolerance(actual, expected, self.config.atol, self.config.rtol)
        absolute_error, relative_error = compute_errors(actual, expected)
        return DiffDetail(
            key=key,
            expected=expected,
            actual=actual,
            raw_actual=match.raw,
            absolute_error=absolute_error,
            relative_error=relative_error,
            allowed_tolerance=allowed_tolerance(
                expected, self.config.atol, self.config.rtol
            ),
            passed=passed,
            unit=unit,
        )

    @staticmethod
    def basis_points(relative_error: float | None) -> float | None:
        """Convert a relative error into basis points (1% = 100 bps)."""
        if relative_error is None:
            return None
        return relative_error * 10_000
