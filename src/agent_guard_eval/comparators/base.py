"""Shared tolerance math used by all comparators."""

from __future__ import annotations


def allowed_tolerance(expected: float, atol: float, rtol: float) -> float:
    """Return the absolute error allowance for ``expected``.

    Formula: ``atol + rtol * |expected|``
    """
    return atol + rtol * abs(expected)


def within_tolerance(actual: float, expected: float, atol: float, rtol: float) -> bool:
    """Return whether ``actual`` is within tolerance of ``expected``."""
    return abs(actual - expected) <= allowed_tolerance(expected, atol, rtol)


def compute_errors(actual: float, expected: float) -> tuple[float, float | None]:
    """Return ``(absolute_error, relative_error)``.

    Relative error is ``None`` when the reference value is zero (division guard).
    """
    absolute_error = abs(actual - expected)
    relative_error = absolute_error / abs(expected) if expected != 0 else None
    return absolute_error, relative_error
