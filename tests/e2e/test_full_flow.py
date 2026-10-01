"""End-to-end tests covering realistic usage."""

from __future__ import annotations

from agent_guard_eval import GuardConfig, GuardPipeline, NumericGuard


def test_e2e_multi_guard_pipeline() -> None:
    numeric = NumericGuard({"Sharpe": 1.5, "Variance": 0.04})
    percent = NumericGuard({"Growth": 12.0}, units={"Growth": "percent"})
    pipeline = GuardPipeline([numeric, percent])
    result = pipeline.validate_all("Sharpe: 1.5, Variance: 0.04, Growth: 12%")
    assert result.is_valid is True
    assert result.violation_count == 0


def test_e2e_blocking_decision() -> None:
    guard = NumericGuard({"Sharpe": 1.5, "Variance": 0.04})
    result = guard.validate("Sharpe: 2.0, Variance: 0.10")
    assert result.is_valid is False
    for violation in result.violations:
        assert violation.key
        assert violation.message


def test_e2e_locale_turkish_style() -> None:
    config = GuardConfig(decimal_sep=",", thousands_sep=".")
    guard = NumericGuard({"Amount": 1234.56}, config=config)
    result = guard.validate("Amount: 1.234,56")
    assert result.is_valid is True


def test_e2e_deterministic_repeatability() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    first = guard.validate("Sharpe: 1.5")
    second = guard.validate("Sharpe: 1.5")
    assert first.to_dict() == second.to_dict()
