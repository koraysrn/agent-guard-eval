"""LangChain / LangGraph integration for the numeric guard.

Requires the optional ``langchain-core`` dependency.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..guard import NumericGuard
from ..report.formatters import to_json

try:
    from langchain_core.tools import BaseTool
    from pydantic import ConfigDict
except ImportError as exc:  # pragma: no cover - depends on optional dependency
    raise ImportError(
        "The LangChain integration requires 'langchain-core' and 'pydantic'. "
        "Install with: pip install 'agent-guard-eval[langchain]'"
    ) from exc


class NumericGuardTool(BaseTool):
    """LangChain tool that validates text against numeric ground truth."""

    name: str = "numeric_guard"
    description: str = (
        "Validate numeric values in the given text against the configured ground truth. "
        "Input must be the raw text to validate."
    )
    guard: NumericGuard

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, text: str) -> str:
        """Run the guard and return the result as JSON."""
        result = self.guard.validate(text)
        return to_json(result)

    async def _arun(self, text: str) -> str:
        """Async variant that delegates to the synchronous run."""
        return self._run(text)


def make_guard_node(
    guard: NumericGuard,
    text_key: str = "text",
    result_key: str = "guard_result",
    valid_key: str = "is_valid",
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Build a LangGraph-compatible node function that guards the given state key."""

    def node(state: dict[str, Any]) -> dict[str, Any]:
        text = state.get(text_key, "")
        result = guard.validate(str(text))
        return {
            result_key: result,
            valid_key: result.is_valid,
        }

    return node
