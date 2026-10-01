"""Regression tests backed by a golden dataset."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_guard_eval import GuardConfig, NumericGuard

_DATA_DIR = Path(__file__).parent / "data"
_CASES = json.loads((_DATA_DIR / "golden_cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _CASES, ids=[case["name"] for case in _CASES])
def test_golden_cases(case: dict) -> None:
    config = GuardConfig(**case.get("config", {}))
    guard = NumericGuard(
        case["ground_truth"], config=config, units=case.get("units")
    )
    result = guard.validate(case["text"])
    assert result.is_valid is case["expected_valid"], case["name"]
    assert result.violation_count == case["expected_violation_count"], case["name"]
