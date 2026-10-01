"""Comparator for currency values with explicit exchange-rate conversion."""

from __future__ import annotations

from ..config import GuardConfig
from ..exceptions import GuardComparisonError
from ..models import DiffDetail, NumericMatch
from .base import allowed_tolerance, compute_errors, within_tolerance


class CurrencyComparator:
    """Compares currency values, converting to the reference unit when a rate exists."""

    def __init__(self, config: GuardConfig) -> None:
        self.config = config

    def compare(
        self,
        key: str,
        match: NumericMatch,
        expected: float,
        unit: str,
    ) -> DiffDetail:
        """Produce a :class:`DiffDetail` for the given currency key and match."""
        actual = match.value
        actual_unit = match.unit or unit

        if actual_unit and actual_unit != unit:
            actual = self._convert(actual, actual_unit, unit)

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

    def _convert(self, amount: float, from_unit: str, to_unit: str) -> float:
        """Convert ``amount`` from ``from_unit`` to ``to_unit`` using configured rates."""
        forward = from_unit + to_unit
        backward = to_unit + from_unit
        if forward in self.config.exchange_rates:
            return amount * self.config.exchange_rates[forward]
        if backward in self.config.exchange_rates:
            return amount / self.config.exchange_rates[backward]
        raise GuardComparisonError(
            f"No exchange rate configured for '{from_unit}' -> '{to_unit}'"
        )
