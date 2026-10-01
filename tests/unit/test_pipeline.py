"""Tests for :mod:`agent_guard_eval.pipeline`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardPipeline, NumericGuard


def test_pipeline_requires_guards() -> None:
    with pytest.raises(ValueError):
        GuardPipeline([])


def test_validate_returns_per_guard() -> None:
    guard1 = NumericGuard({"A": 1.0})
    guard2 = NumericGuard({"B": 2.0})
    pipeline = GuardPipeline([guard1, guard2])
    results = pipeline.validate("A: 1.0, B: 2.0")
    assert len(results) == 2
    assert all(result.is_valid for result in results)


def test_validate_all_aggregates() -> None:
    guard1 = NumericGuard({"A": 1.0})
    guard2 = NumericGuard({"B": 99.0})
    pipeline = GuardPipeline([guard1, guard2])
    result = pipeline.validate_all("A: 1.0, B: 2.0")
    assert result.is_valid is False
    assert result.violation_count == 1
    assert result.details["guard_count"] == 2


def test_validate_all_passes_when_all_pass() -> None:
    guard1 = NumericGuard({"A": 1.0})
    guard2 = NumericGuard({"B": 2.0})
    pipeline = GuardPipeline([guard1, guard2])
    result = pipeline.validate_all("A: 1.0, B: 2.0")
    assert result.is_valid is True
    assert result.violation_count == 0
