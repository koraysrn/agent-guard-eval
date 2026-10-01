"""Pipeline for chaining multiple guards against the same text."""

from __future__ import annotations

from collections.abc import Sequence

from .guard import NumericGuard
from .models import ValidationResult


class GuardPipeline:
    """Runs several guards and aggregates their individual results."""

    def __init__(self, guards: Sequence[NumericGuard]) -> None:
        if not guards:
            raise ValueError("GuardPipeline requires at least one guard")
        self.guards = list(guards)

    def validate(self, text: str) -> list[ValidationResult]:
        """Run every guard and return their individual results."""
        return [guard.validate(text) for guard in self.guards]

    def validate_all(self, text: str) -> ValidationResult:
        """Run every guard and return a single aggregated result."""
        results = self.validate(text)
        violations = tuple(
            violation for result in results for violation in result.violations
        )
        is_valid = all(result.is_valid for result in results)
        details = {
            "guard_count": len(results),
            "per_guard": [
                {
                    "index": index,
                    "is_valid": result.is_valid,
                    "violation_count": result.violation_count,
                }
                for index, result in enumerate(results)
            ],
        }
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            details=details,
            text_length=len(text),
            extracted_count=max(
                (result.extracted_count for result in results), default=0
            ),
        )
