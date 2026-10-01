"""Tests for :mod:`agent_guard_eval.guard`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig, NumericGuard
from agent_guard_eval.exceptions import GuardInputError
from agent_guard_eval.models import ViolationType


def test_valid_text_passes() -> None:
    guard = NumericGuard({"Sharpe": 1.5, "Variance": 0.04})
    result = guard.validate("Sharpe: 1.5, Variance: 0.04")
    assert result.is_valid is True
    assert result.extracted_count == 2
    assert result.text_length == len("Sharpe: 1.5, Variance: 0.04")


def test_mismatch_fails() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    result = guard.validate("Sharpe: 1.9")
    assert result.is_valid is False
    assert result.violations[0].violation_type is ViolationType.MISMATCH


def test_missing_key_fails() -> None:
    guard = NumericGuard({"Sharpe": 1.5, "Variance": 0.04})
    result = guard.validate("Sharpe: 1.5")
    assert result.is_valid is False
    types = {violation.violation_type for violation in result.violations}
    assert ViolationType.MISSING in types


def test_strict_missing_disabled() -> None:
    config = GuardConfig(strict_missing=False)
    guard = NumericGuard({"Sharpe": 1.5, "Variance": 0.04}, config=config)
    result = guard.validate("Sharpe: 1.5")
    assert result.is_valid is True


def test_unexpected_reporting() -> None:
    config = GuardConfig(report_unexpected=True)
    guard = NumericGuard({"Sharpe": 1.5}, config=config)
    result = guard.validate("Sharpe: 1.5 and extra 99")
    types = {violation.violation_type for violation in result.violations}
    assert ViolationType.UNEXPECTED in types


def test_unexpected_disabled_by_default() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    result = guard.validate("Sharpe: 1.5 and extra 99")
    assert result.is_valid is True


def test_input_type_error() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    with pytest.raises(GuardInputError):
        guard.validate(None)  # type: ignore[arg-type]


def test_oversized_input_error() -> None:
    guard = NumericGuard({"Sharpe": 1.5}, config=GuardConfig(max_input_chars=5))
    with pytest.raises(GuardInputError):
        guard.validate("Sharpe: 1.5")


def test_percentage_key_via_units() -> None:
    guard = NumericGuard({"Growth": 15.0}, units={"Growth": "percent"})
    result = guard.validate("Growth: 15%")
    assert result.is_valid is True


def test_percentage_fraction_scale() -> None:
    config = GuardConfig(percent_as_fraction=True)
    guard = NumericGuard({"Growth": 0.15}, config=config, units={"Growth": "percent"})
    result = guard.validate("Growth: 15%")
    assert result.is_valid is True


def test_currency_key_via_units() -> None:
    config = GuardConfig(exchange_rates={"EURUSD": 1.1})
    guard = NumericGuard({"Price": 11.0}, config=config, units={"Price": "USD"})
    result = guard.validate("Price: 10 EUR")
    assert result.is_valid is True


def test_all_extractors_disabled_yields_missing() -> None:
    config = GuardConfig(
        enable_number=False,
        enable_percentage=False,
        enable_currency=False,
        enable_ratio=False,
    )
    guard = NumericGuard({"Sharpe": 1.5}, config=config)
    result = guard.validate("Sharpe: 1.5")
    assert result.is_valid is False
    assert result.extracted_count == 0
