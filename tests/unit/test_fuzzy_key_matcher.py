"""Tests for :mod:`agent_guard_eval.matchers.fuzzy_key_matcher`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.matchers.fuzzy_key_matcher import FuzzyKeyMatcher
from agent_guard_eval.models import NumericMatch


def test_typo_key_resolved() -> None:
    text = "The Sharpa is 1.5"
    matches = [NumericMatch("", 1.5, "1.5", 12, 15, "number")]
    result = FuzzyKeyMatcher(GuardConfig()).match(text, matches, ["Sharpe"])
    assert "Sharpe" in result
    assert result["Sharpe"].value == 1.5


def test_no_close_match() -> None:
    text = "The ratio is 1.5"
    matches = [NumericMatch("", 1.5, "1.5", 13, 16, "number")]
    result = FuzzyKeyMatcher(GuardConfig()).match(text, matches, ["Sharpe"])
    assert "Sharpe" not in result


def test_cutoff_controls_matching() -> None:
    text = "The Sharpe is 1.5"
    matches = [NumericMatch("", 1.5, "1.5", 12, 15, "number")]
    result = FuzzyKeyMatcher(GuardConfig(fuzzy_cutoff=0.99)).match(
        text, matches, ["Sharpee"]
    )
    assert "Sharpee" not in result


def test_empty_matches() -> None:
    result = FuzzyKeyMatcher(GuardConfig()).match("Sharpe", [], ["Sharpe"])
    assert result == {}
