"""Exception hierarchy for the ``agent_guard_eval`` package.

All custom exceptions derive from :class:`GuardError`, so callers can catch every
package-specific error with a single ``except GuardError`` clause.
"""

from __future__ import annotations


class GuardError(Exception):
    """Base class for every error raised by this package."""

    default_message = "agent_guard_eval error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class GuardConfigurationError(GuardError):
    """Raised when the configuration is invalid (negative tolerance, broken pattern, etc.)."""

    default_message = "Invalid guard configuration"


class GuardInputError(GuardError):
    """Raised when the validation input is invalid (``None``, oversized text, etc.)."""

    default_message = "Invalid validation input"


class GuardExtractionError(GuardError):
    """Raised for errors that occur during numeric extraction."""

    default_message = "Numeric extraction error"


class GuardMatchingError(GuardError):
    """Raised for errors that occur during concept matching."""

    default_message = "Concept matching error"


class GuardComparisonError(GuardError):
    """Raised for errors that occur during comparison (e.g. missing exchange rate)."""

    default_message = "Comparison error"


class GuardTimeoutError(GuardError):
    """Raised when a validation sub-step exceeds its time budget."""

    default_message = "Validation timed out"


class GuardIntegrationError(GuardError):
    """Raised for external integration (LangChain, FastAPI) errors."""

    default_message = "Integration error"
