"""Tests for :mod:`agent_guard_eval.extractors.base`."""

from __future__ import annotations

import pytest

from agent_guard_eval import GuardConfig
from agent_guard_eval.exceptions import GuardExtractionError
from agent_guard_eval.extractors.base import SafeRegex, compile_pattern, normalize_number


def test_compile_pattern_valid() -> None:
    pattern = compile_pattern("test", r"\d+")
    assert pattern.match("123") is not None


def test_compile_pattern_invalid() -> None:
    with pytest.raises(GuardExtractionError):
        compile_pattern("bad", "(")


def test_normalize_number_plain() -> None:
    assert normalize_number("1.5", ".", ",") == 1.5


def test_normalize_number_locale() -> None:
    assert normalize_number("1.234,56", ",", ".") == 1234.56


def test_normalize_number_signed() -> None:
    assert normalize_number("-3.25", ".", ",") == -3.25
    assert normalize_number("+3.25", ".", ",") == 3.25


def test_normalize_number_scientific() -> None:
    assert normalize_number("1.5e-3", ".", ",") == 0.0015


def test_safe_regex_size_guard() -> None:
    regex = SafeRegex("num", r"\d+", GuardConfig(max_input_chars=5))
    with pytest.raises(GuardExtractionError):
        list(regex.finditer("123456"))


def test_safe_regex_finditer() -> None:
    regex = SafeRegex("num", r"\d+", GuardConfig())
    assert [m.group(0) for m in regex.finditer("a1b22")] == ["1", "22"]


def test_safe_regex_search() -> None:
    regex = SafeRegex("num", r"\d+", GuardConfig())
    match = regex.search("abc42")
    assert match is not None
    assert match.group(0) == "42"
