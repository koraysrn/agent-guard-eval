"""Tests for :mod:`agent_guard_eval.extractors.percentage_extractor`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.extractors.percentage_extractor import PercentageExtractor


def _extract(text: str, config: GuardConfig | None = None):
    extractor = PercentageExtractor(config or GuardConfig())
    return [(match.value, match.unit) for match in extractor.extract(text)]


def test_trailing_percent() -> None:
    assert _extract("Growth 15%") == [(15.0, "%")]


def test_spaced_percent() -> None:
    assert _extract("Growth 15 %") == [(15.0, "%")]


def test_leading_percent() -> None:
    assert _extract("Growth %15") == [(15.0, "%")]


def test_word_percent() -> None:
    assert _extract("Growth percent 12.5") == [(12.5, "%")]


def test_negative_percent() -> None:
    assert _extract("Drawdown -23%") == [(-23.0, "%")]


def test_multiple_percentages() -> None:
    assert _extract("A 10%, B 20%, C 30%") == [(10.0, "%"), (20.0, "%"), (30.0, "%")]


def test_locale_decimal_comma() -> None:
    config = GuardConfig(decimal_sep=",", thousands_sep=".")
    assert _extract("Growth 12,5%", config) == [(12.5, "%")]


def test_no_percentage() -> None:
    assert _extract("No percentage here") == []
