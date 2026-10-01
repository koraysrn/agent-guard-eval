"""Tests for :mod:`agent_guard_eval.extractors.currency_extractor`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.extractors.currency_extractor import CurrencyExtractor


def _extract(text: str, config: GuardConfig | None = None):
    extractor = CurrencyExtractor(config or GuardConfig())
    return [(match.value, match.unit) for match in extractor.extract(text)]


def test_symbol_leading() -> None:
    assert _extract("Price $1,234.56") == [(1234.56, "USD")]


def test_symbol_trailing() -> None:
    assert _extract("Price 99 ₺") == [(99.0, "TRY")]


def test_euro_symbol() -> None:
    assert _extract("Price €10.5") == [(10.5, "EUR")]


def test_iso_code_trailing() -> None:
    assert _extract("Price 100 EUR") == [(100.0, "EUR")]


def test_iso_code_leading() -> None:
    assert _extract("Price EUR 100") == [(100.0, "EUR")]


def test_locale_grouped() -> None:
    config = GuardConfig(decimal_sep=",", thousands_sep=".")
    assert _extract("Price 1.234,56 €", config) == [(1234.56, "EUR")]


def test_negative_amount() -> None:
    assert _extract("Change -$5.00") == [(-5.0, "USD")]


def test_no_currency() -> None:
    assert _extract("Just a number 12.5") == []
