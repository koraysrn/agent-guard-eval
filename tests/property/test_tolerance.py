"""Property-based tests for the tolerance formula."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from agent_guard_eval.comparators.base import (
    allowed_tolerance,
    compute_errors,
    within_tolerance,
)


@given(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False),
)
def test_exact_value_always_within_tolerance(value: float, atol: float, rtol: float) -> None:
    assert within_tolerance(value, value, atol, rtol) is True


@given(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6),
    st.floats(min_value=0, max_value=0.5, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0, max_value=0.5, allow_nan=False, allow_infinity=False),
)
def test_allowed_tolerance_formula(expected: float, atol: float, rtol: float) -> None:
    allowance = allowed_tolerance(expected, atol, rtol)
    assert allowance >= 0
    assert allowance == atol + rtol * abs(expected)


@given(
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e6, max_value=1e6)
)
def test_compute_errors_non_negative(expected: float) -> None:
    absolute_error, relative_error = compute_errors(expected, expected)
    assert absolute_error >= 0
    if expected == 0:
        assert relative_error is None
    else:
        assert relative_error == 0
