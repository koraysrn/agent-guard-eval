"""Tests for :mod:`agent_guard_eval.comparators.base`."""

from __future__ import annotations

import pytest

from agent_guard_eval.comparators.base import (
    allowed_tolerance,
    compute_errors,
    within_tolerance,
)


def test_allowed_tolerance() -> None:
    assert allowed_tolerance(100.0, atol=1e-6, rtol=1e-4) == pytest.approx(0.010001)


def test_allowed_tolerance_zero_reference() -> None:
    assert allowed_tolerance(0.0, atol=1e-6, rtol=1e-4) == pytest.approx(1e-6)


def test_within_tolerance_true() -> None:
    assert within_tolerance(1.50001, 1.5, 1e-6, 1e-4) is True


def test_within_tolerance_false() -> None:
    assert within_tolerance(1.9, 1.5, 1e-6, 1e-4) is False


def test_within_tolerance_zero_reference() -> None:
    assert within_tolerance(0.0, 0.0, 1e-6, 1e-4) is True
    assert within_tolerance(1e-7, 0.0, 1e-6, 1e-4) is True
    assert within_tolerance(1e-3, 0.0, 1e-6, 1e-4) is False


def test_compute_errors() -> None:
    absolute_error, relative_error = compute_errors(2.0, 1.0)
    assert absolute_error == 1.0
    assert relative_error == 1.0


def test_compute_errors_zero_reference() -> None:
    absolute_error, relative_error = compute_errors(0.0, 0.0)
    assert absolute_error == 0.0
    assert relative_error is None
