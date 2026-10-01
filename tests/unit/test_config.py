"""Tests for :mod:`agent_guard_eval.config`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.exceptions import GuardConfigurationError


def test_defaults() -> None:
    config = GuardConfig()
    assert config.atol == 1e-6
    assert config.rtol == 1e-4
    assert config.max_input_chars == 100_000
    assert config.decimal_sep == "."
    assert config.thousands_sep == ","


def test_custom_values() -> None:
    config = GuardConfig(atol=1e-3, rtol=0.05, max_input_chars=500)
    assert config.atol == 1e-3
    assert config.rtol == 0.05
    assert config.max_input_chars == 500


@pytest.mark.parametrize(
    "kwargs",
    [
        {"atol": -0.1},
        {"rtol": -0.1},
        {"rtol": 1.5},
        {"max_input_chars": 0},
        {"decimal_sep": ",", "thousands_sep": ","},
        {"decimal_sep": "..", "thousands_sep": ","},
        {"fuzzy_cutoff": 1.5},
        {"fuzzy_cutoff": -0.1},
        {"max_match_distance": -1},
        {"exchange_rates": {"EURUSD": 0.0}},
        {"exchange_rates": {"EURUSD": -1.0}},
    ],
)
def test_invalid_config_raises(kwargs: dict) -> None:
    with pytest.raises(GuardConfigurationError):
        GuardConfig(**kwargs)


def test_is_extractor_enabled() -> None:
    config = GuardConfig(enable_ratio=False, enable_currency=False)
    assert config.is_extractor_enabled("ratio") is False
    assert config.is_extractor_enabled("currency") is False
    assert config.is_extractor_enabled("number") is True
    assert config.is_extractor_enabled("percentage") is True
    assert config.is_extractor_enabled("unknown") is False


def test_immutability() -> None:
    config = GuardConfig()
    with pytest.raises(AttributeError):
        config.atol = 0.5  # type: ignore[misc]
