"""Shared pytest fixtures and sample data."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig, NumericGuard

SAMPLE_GROUND_TRUTH: dict[str, float] = {
    "Sharpe": 1.5,
    "Variance": 0.04,
    "Annual Return": 12.0,
    "Max Drawdown": -23.0,
}

VALID_TEXT = (
    "The portfolio reports Sharpe: 1.5, Variance: 0.04, "
    "Annual Return: 12%, Max Drawdown: -23%."
)

INVALID_TEXT = (
    "The portfolio reports Sharpe: 1.9, Variance: 0.07, "
    "Annual Return: 15%, Max Drawdown: -30%."
)


@pytest.fixture
def config() -> GuardConfig:
    return GuardConfig()


@pytest.fixture
def sample_ground_truth() -> dict[str, float]:
    return dict(SAMPLE_GROUND_TRUTH)


@pytest.fixture
def valid_text() -> str:
    return VALID_TEXT


@pytest.fixture
def invalid_text() -> str:
    return INVALID_TEXT


@pytest.fixture
def guard(sample_ground_truth: dict[str, float]) -> NumericGuard:
    return NumericGuard(sample_ground_truth)
