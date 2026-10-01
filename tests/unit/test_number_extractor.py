"""Tests for :mod:`agent_guard_eval.extractors.number_extractor`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.extractors.number_extractor import NumberExtractor


def _extract(text: str, config: GuardConfig | None = None) -> list[float]:
    extractor = NumberExtractor(config or GuardConfig())
    return [match.value for match in extractor.extract(text)]


def test_integers() -> None:
    assert _extract("The value is 42 and 7.") == [42.0, 7.0]


def test_decimals() -> None:
    assert _extract("Ratio 1.5 and 0.04") == [1.5, 0.04]


def test_negative_numbers() -> None:
    assert _extract("Drawdown -23.5 and +10") == [-23.5, 10.0]


def test_scientific_notation() -> None:
    assert _extract("Probability 1.5e-3") == [0.0015]


def test_grouped_thousands() -> None:
    assert _extract("Amount 1,234,567.89") == [1234567.89]


def test_locale_decimal_comma() -> None:
    config = GuardConfig(decimal_sep=",", thousands_sep=".")
    assert _extract("Amount 1.234,56", config) == [1234.56]


def test_percent_sign_excluded() -> None:
    assert _extract("Growth 15%") == []


def test_currency_symbol_excluded() -> None:
    assert _extract("Price $12.5") == []


def test_sentence_punctuation_after_number() -> None:
    assert _extract("Value is 1.5, and then 2.0.") == [1.5, 2.0]


def test_no_numbers() -> None:
    assert _extract("nothing here") == []
