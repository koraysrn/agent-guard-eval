"""Integration tests for the LangChain adapter."""

from __future__ import annotations

import pytest

pytest.importorskip("langchain_core")

from agent_guard_eval import NumericGuard
from agent_guard_eval.integrations.langchain import (
    NumericGuardTool,
    make_guard_node,
)


def test_tool_runs_guard() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    tool = NumericGuardTool(guard=guard)
    output = tool._run("Sharpe: 1.5")
    assert "is_valid" in output


def test_tool_invokes_guard_via_invoke() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    tool = NumericGuardTool(guard=guard)
    result = tool.invoke("Sharpe: 1.5")
    assert "is_valid" in result


def test_make_guard_node() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    node = make_guard_node(guard)
    state = node({"text": "Sharpe: 1.5"})
    assert state["is_valid"] is True
    assert state["guard_result"].is_valid is True


def test_make_guard_node_invalid() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    node = make_guard_node(guard)
    state = node({"text": "Sharpe: 1.9"})
    assert state["is_valid"] is False
