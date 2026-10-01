"""agent_guard_eval: deterministic numeric validation (guardrail) library.

This package extracts numeric expressions from LLM-generated text, matches them against
a reference dictionary and compares them using ``atol`` / ``rtol`` tolerances. No LLM is
used during validation; every decision is rule-based and deterministic.
"""

from .config import GuardConfig
from .exceptions import (
    GuardComparisonError,
    GuardConfigurationError,
    GuardError,
    GuardExtractionError,
    GuardInputError,
    GuardIntegrationError,
    GuardMatchingError,
    GuardTimeoutError,
)
from .guard import NumericGuard
from .models import (
    DiffDetail,
    GuardViolation,
    NumericMatch,
    ValidationResult,
    ViolationType,
)
from .pipeline import GuardPipeline

__all__ = [
    "DiffDetail",
    "GuardComparisonError",
    "GuardConfig",
    "GuardConfigurationError",
    "GuardError",
    "GuardExtractionError",
    "GuardInputError",
    "GuardIntegrationError",
    "GuardMatchingError",
    "GuardPipeline",
    "GuardTimeoutError",
    "GuardViolation",
    "NumericGuard",
    "NumericMatch",
    "ValidationResult",
    "ViolationType",
]

__version__ = "1.0.0"
