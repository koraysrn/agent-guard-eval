"""Tests for the Matcher base class."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.matchers.base import Matcher


def test_matcher_is_abstract() -> None:
    with pytest.raises(TypeError):
        Matcher(GuardConfig())  # type: ignore[abstract]
