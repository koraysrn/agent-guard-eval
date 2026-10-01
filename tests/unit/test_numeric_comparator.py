"""Tests for :mod:`agent_guard_eval.comparators.numeric_comparator`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.comparators.numeric_comparator import NumericComparator
from agent_guard_eval.models import NumericMatch


def test_passing_comparison() -> None:
    comparator = NumericComparator(GuardConfig())
    match = NumericMatch("", 1.5, "1.5", 0, 3, "number")
    diff = comparator.compare("Sharpe", match, 1.5)
    assert diff.passed is True
    assert diff.absolute_error == 0.0
    assert diff.relative_error == 0.0


def test_failing_comparison() -> None:
    comparator = NumericComparator(GuardConfig())
    match = NumericMatch("", 1.9, "1.9", 0, 3, "number")
    diff = comparator.compare("Sharpe", match, 1.5)
    assert diff.passed is False
    assert diff.absolute_error == pytest.approx(0.4)


def test_unit_falls_back_to_match_unit() -> None:
    comparator = NumericComparator(GuardConfig())
    match = NumericMatch("", 1.5, "1.5", 0, 3, "number", unit="ratio")
    diff = comparator.compare("Ratio", match, 1.5)
    assert diff.unit == "ratio"
