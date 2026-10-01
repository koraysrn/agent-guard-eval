"""Format validation results as JSON, Markdown or Rich tables."""

from __future__ import annotations

import json

from ..models import ValidationResult


def _fmt(value: object) -> str:
    """Format a possibly-``None`` numeric value for display."""
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def to_json(result: ValidationResult, indent: int = 2) -> str:
    """Serialize a :class:`ValidationResult` as pretty JSON."""
    return json.dumps(result.to_dict(), indent=indent, ensure_ascii=False, default=str)


def to_markdown(result: ValidationResult) -> str:
    """Render a :class:`ValidationResult` as a Markdown report."""
    lines = [
        f"# Validation Result: {'PASS' if result.is_valid else 'FAIL'}",
        "",
        f"- Valid: {result.is_valid}",
        f"- Violations: {result.violation_count}",
        f"- Extracted numeric values: {result.extracted_count}",
        f"- Text length: {result.text_length}",
        "",
    ]
    if result.violations:
        lines.append(
            "| # | Type | Key | Expected | Actual | Raw | Abs. Error | Allowed | Message |"
        )
        lines.append(
            "|---|------|-----|----------|--------|-----|------------|---------|---------|"
        )
        for index, violation in enumerate(result.violations, start=1):
            lines.append(
                f"| {index} | {violation.violation_type.value} | {violation.key} | "
                f"{_fmt(violation.expected)} | {_fmt(violation.actual)} | "
                f"{violation.raw_actual} | {_fmt(violation.absolute_error)} | "
                f"{_fmt(violation.allowed_tolerance)} | {violation.message} |"
            )
    else:
        lines.append("No violations.")
    return "\n".join(lines)


def to_rich_table(result: ValidationResult) -> str:
    """Render a :class:`ValidationResult` as an ANSI-free Rich table string."""
    from rich.console import Console
    from rich.table import Table

    console = Console(force_terminal=False, width=140, record=True)
    table = Table(title=f"Validation Result: {'PASS' if result.is_valid else 'FAIL'}")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Expected", justify="right", style="green")
    table.add_column("Actual", justify="right", style="red")
    table.add_column("Raw", style="yellow")
    table.add_column("Abs. Error", justify="right")
    table.add_column("Allowed", justify="right")
    table.add_column("Message", style="dim")

    if result.violations:
        for violation in result.violations:
            table.add_row(
                violation.key,
                violation.violation_type.value,
                _fmt(violation.expected),
                _fmt(violation.actual),
                str(violation.raw_actual),
                _fmt(violation.absolute_error),
                _fmt(violation.allowed_tolerance),
                violation.message,
            )
    else:
        table.add_row("-", "-", "-", "-", "-", "-", "-", "No violations")

    console.print(table)
    return console.export_text()
