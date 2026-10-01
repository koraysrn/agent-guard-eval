"""Integration test for the full extract -> match -> compare -> report chain."""

from __future__ import annotations

from agent_guard_eval import NumericGuard
from agent_guard_eval.report.formatters import to_json, to_markdown


def test_full_chain_valid_and_invalid() -> None:
    guard = NumericGuard(
        {"Sharpe": 1.5, "Variance": 0.04, "Growth": 15.0},
        units={"Growth": "percent"},
    )

    valid = guard.validate("Sharpe: 1.5, Variance: 0.04, Growth: 15%")
    assert valid.is_valid is True
    assert valid.details["matched_keys"] == ["Growth", "Sharpe", "Variance"]

    invalid = guard.validate("Sharpe: 2.0, Variance: 0.04, Growth: 12%")
    assert invalid.is_valid is False

    markdown = to_markdown(invalid)
    assert "FAIL" in markdown
    assert "Sharpe" in markdown

    payload = to_json(invalid)
    assert "violations" in payload


def test_report_contains_actionable_diff() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    result = guard.validate("Sharpe: 1.9")
    violation = result.violations[0]
    assert violation.expected == 1.5
    assert violation.actual == 1.9
    assert violation.absolute_error is not None
    assert violation.allowed_tolerance is not None
    assert "Sharpe" in violation.message
