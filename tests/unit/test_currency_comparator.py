"""Tests for :mod:`agent_guard_eval.comparators.currency_comparator`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.comparators.currency_comparator import CurrencyComparator
from agent_guard_eval.exceptions import GuardComparisonError
from agent_guard_eval.models import NumericMatch


def test_same_unit_no_conversion() -> None:
    comparator = CurrencyComparator(GuardConfig())
    match = NumericMatch("", 100.0, "100", 0, 3, "currency", unit="USD")
    diff = comparator.compare("Price", match, 100.0, unit="USD")
    assert diff.passed is True


def test_conversion_forward() -> None:
    config = GuardConfig(exchange_rates={"EURUSD": 1.1})
    comparator = CurrencyComparator(config)
    match = NumericMatch("", 10.0, "10", 0, 2, "currency", unit="EUR")
    diff = comparator.compare("Price", match, 11.0, unit="USD")
    assert diff.passed is True


def test_conversion_backward() -> None:
    config = GuardConfig(exchange_rates={"EURUSD": 1.1})
    comparator = CurrencyComparator(config)
    match = NumericMatch("", 11.0, "11", 0, 2, "currency", unit="USD")
    diff = comparator.compare("Price", match, 10.0, unit="EUR")
    assert diff.passed is True


def test_missing_rate_raises() -> None:
    comparator = CurrencyComparator(GuardConfig())
    match = NumericMatch("", 10.0, "10", 0, 2, "currency", unit="EUR")
    with pytest.raises(GuardComparisonError):
        comparator.compare("Price", match, 10.0, unit="USD")
