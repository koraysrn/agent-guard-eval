"""Tests for :mod:`agent_guard_eval.extractors.ratio_extractor`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.extractors.ratio_extractor import RatioExtractor


def _extract(text: str):
    extractor = RatioExtractor(GuardConfig())
    return [(match.value, match.unit) for match in extractor.extract(text)]


def test_colon_ratio() -> None:
    assert _extract("The ratio is 3:1") == [(3.0, "ratio")]


def test_slash_ratio() -> None:
    assert _extract("The ratio is 3/4") == [(0.75, "ratio")]


def test_multiple_ratios() -> None:
    assert _extract("Ratios 1:2 and 3/4") == [(0.5, "ratio"), (0.75, "ratio")]


def test_date_like_rejected() -> None:
    assert _extract("On 3/4/2024 the value was") == []


def test_zero_denominator_skipped() -> None:
    assert _extract("Ratio 3:0") == []


def test_no_ratio() -> None:
    assert _extract("Nothing to see here") == []
