"""Diff generation and result formatting."""

from .diff import (
    build_mismatch_violation,
    build_missing_violation,
    build_unexpected_violation,
)
from .formatters import to_json, to_markdown, to_rich_table

__all__ = [
    "build_mismatch_violation",
    "build_missing_violation",
    "build_unexpected_violation",
    "to_json",
    "to_markdown",
    "to_rich_table",
]
