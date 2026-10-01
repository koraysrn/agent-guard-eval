"""Tests for :mod:`agent_guard_eval.exceptions`."""

from __future__ import annotations

import pytest

from agent_guard_eval.exceptions import (
    GuardComparisonError,
    GuardConfigurationError,
    GuardError,
    GuardExtractionError,
    GuardInputError,
    GuardIntegrationError,
    GuardMatchingError,
    GuardTimeoutError,
)


def test_all_exceptions_derive_from_guard_error() -> None:
    for exc_cls in [
        GuardConfigurationError,
        GuardInputError,
        GuardExtractionError,
        GuardMatchingError,
        GuardComparisonError,
        GuardTimeoutError,
        GuardIntegrationError,
    ]:
        assert issubclass(exc_cls, GuardError)


def test_default_messages() -> None:
    assert str(GuardConfigurationError()) == "Invalid guard configuration"
    assert str(GuardInputError()) == "Invalid validation input"
    assert str(GuardExtractionError()) == "Numeric extraction error"


def test_custom_message() -> None:
    assert str(GuardInputError("custom message")) == "custom message"


def test_catch_all_via_base() -> None:
    with pytest.raises(GuardError):
        raise GuardComparisonError()
