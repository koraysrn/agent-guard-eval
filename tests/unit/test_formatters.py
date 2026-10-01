"""Tests for :mod:`agent_guard_eval.report.formatters`."""

from __future__ import annotations

import json

from agent_guard_eval.models import GuardViolation, ValidationResult, ViolationType
from agent_guard_eval.report.formatters import to_json, to_markdown, to_rich_table


def _valid_result() -> ValidationResult:
    return ValidationResult(is_valid=True, text_length=5, extracted_count=1)


def _invalid_result() -> ValidationResult:
    violation = GuardViolation(
        violation_type=ViolationType.MISMATCH,
        key="Sharpe",
        message="mismatch",
        expected=1.5,
        actual=1.9,
    )
    return ValidationResult(
        is_valid=False, violations=(violation,), text_length=5, extracted_count=1
    )


def test_to_json_valid() -> None:
    payload = json.loads(to_json(_valid_result()))
    assert payload["is_valid"] is True
    assert payload["violation_count"] == 0


def test_to_json_invalid_has_violations() -> None:
    payload = json.loads(to_json(_invalid_result()))
    assert payload["is_valid"] is False
    assert len(payload["violations"]) == 1


def test_to_markdown_contains_pass() -> None:
    markdown = to_markdown(_valid_result())
    assert "PASS" in markdown
    assert "No violations" in markdown


def test_to_markdown_contains_fail() -> None:
    markdown = to_markdown(_invalid_result())
    assert "FAIL" in markdown
    assert "Sharpe" in markdown


def test_to_rich_table_non_empty() -> None:
    rich = to_rich_table(_invalid_result())
    assert "Sharpe" in rich
    assert "FAIL" in rich
