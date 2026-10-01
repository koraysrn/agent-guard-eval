"""Tests for :mod:`agent_guard_eval.comparators.percentage_comparator`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.comparators.percentage_comparator import PercentageComparator
from agent_guard_eval.models import NumericMatch


def test_percent_scale_pass() -> None:
    comparator = PercentageComparator(GuardConfig())
    match = NumericMatch("", 15.0, "15%", 0, 3, "percentage", unit="%")
    diff = comparator.compare("Growth", match, 15.0)
    assert diff.passed is True


def test_percent_scale_fail() -> None:
    comparator = PercentageComparator(GuardConfig())
    match = NumericMatch("", 20.0, "20%", 0, 3, "percentage", unit="%")
    diff = comparator.compare("Growth", match, 15.0)
    assert diff.passed is False


def test_fraction_scale_converts() -> None:
    config = GuardConfig(percent_as_fraction=True)
    comparator = PercentageComparator(config)
    match = NumericMatch("", 15.0, "15%", 0, 3, "percentage", unit="%")
    diff = comparator.compare("Growth", match, 0.15)
    assert diff.passed is True
    assert diff.actual == pytest.approx(0.15)


def test_fraction_scale_fail() -> None:
    config = GuardConfig(percent_as_fraction=True)
    comparator = PercentageComparator(config)
    match = NumericMatch("", 20.0, "20%", 0, 3, "percentage", unit="%")
    diff = comparator.compare("Growth", match, 0.15)
    assert diff.passed is False


def test_basis_points() -> None:
    assert PercentageComparator.basis_points(0.01) == pytest.approx(100.0)
    assert PercentageComparator.basis_points(None) is None
