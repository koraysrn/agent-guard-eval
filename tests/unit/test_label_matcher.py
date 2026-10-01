"""Tests for :mod:`agent_guard_eval.matchers.label_matcher`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.matchers.label_matcher import LabelMatcher
from agent_guard_eval.models import NumericMatch


def _match(text: str, matches: list[NumericMatch], keys: list[str]):
    return LabelMatcher(GuardConfig()).match(text, matches, keys)


def test_colon_label() -> None:
    matches = [NumericMatch("", 1.5, "1.5", 8, 11, "number")]
    result = _match("Sharpe: 1.5", matches, ["Sharpe"])
    assert "Sharpe" in result
    assert result["Sharpe"].value == 1.5


def test_equals_label() -> None:
    matches = [NumericMatch("", 2.1, "2.1", 12, 15, "number")]
    result = _match("Variance = 2.1", matches, ["Variance"])
    assert result["Variance"].value == 2.1


def test_case_insensitive() -> None:
    matches = [NumericMatch("", 1.5, "1.5", 8, 11, "number")]
    result = _match("sharpe: 1.5", matches, ["Sharpe"])
    assert "Sharpe" in result


def test_nearest_value_after_label() -> None:
    matches = [
        NumericMatch("", 1.5, "1.5", 8, 11, "number"),
        NumericMatch("", 2.0, "2.0", 20, 23, "number"),
    ]
    result = _match("Sharpe: 1.5, other: 2.0", matches, ["Sharpe"])
    assert result["Sharpe"].value == 1.5


def test_missing_label_returns_empty() -> None:
    matches = [NumericMatch("", 1.5, "1.5", 0, 3, "number")]
    assert _match("no label 1.5", matches, ["Sharpe"]) == {}
