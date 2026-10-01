"""Tests for :mod:`agent_guard_eval.matchers.proximity_matcher`."""

from __future__ import annotations

from agent_guard_eval import GuardConfig
from agent_guard_eval.matchers.proximity_matcher import ProximityMatcher
from agent_guard_eval.models import NumericMatch


def test_closest_key_assigned() -> None:
    text = "The Sharpe is 1.5 and the Variance is 0.04"
    matches = [
        NumericMatch("", 1.5, "1.5", 14, 17, "number"),
        NumericMatch("", 0.04, "0.04", 38, 42, "number"),
    ]
    result = ProximityMatcher(GuardConfig()).match(text, matches, ["Sharpe", "Variance"])
    assert result["Sharpe"].value == 1.5
    assert result["Variance"].value == 0.04


def test_distance_bound_respected() -> None:
    text = "Sharpe is 1.5"
    matches = [NumericMatch("", 1.5, "1.5", 12, 15, "number")]
    result = ProximityMatcher(GuardConfig(max_match_distance=2)).match(
        text, matches, ["Sharpe"]
    )
    assert "Sharpe" not in result


def test_word_boundaries_respected() -> None:
    text = "The Sharpey is 1.5"
    matches = [NumericMatch("", 1.5, "1.5", 14, 17, "number")]
    result = ProximityMatcher(GuardConfig()).match(text, matches, ["Sharpe"])
    assert "Sharpe" not in result


def test_empty_matches() -> None:
    result = ProximityMatcher(GuardConfig()).match("Sharpe", [], ["Sharpe"])
    assert result == {}
