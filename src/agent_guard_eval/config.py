"""Parametric configuration for the validation layer.

Every threshold and behavior switch lives in this single class, so different use
cases can be configured without touching any code.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .exceptions import GuardConfigurationError


@dataclass(frozen=True, slots=True)
class GuardConfig:
    """Parametric configuration for deterministic validation.

    Tolerance formula: ``|V_text - V_reference| <= atol + rtol * |V_reference|``
    """

    # Tolerance parameters
    atol: float = 1e-6
    """Absolute tolerance. The only safety bound when the reference value is zero."""
    rtol: float = 1e-4
    """Relative tolerance (proportional error allowance)."""
    max_rtol: float = 1.0
    """Upper bound for ``rtol``; prevents overly permissive tolerances."""

    # Input safety
    max_input_chars: int = 100_000
    """Character limit that blocks oversized inputs (DoS protection)."""

    # Locale support
    decimal_sep: str = "."
    """Decimal separator (``.`` or ``,``)."""
    thousands_sep: str = ","
    """Thousands separator (``,`` or ``.``)."""

    # Which extractors are active
    enable_number: bool = True
    enable_percentage: bool = True
    enable_currency: bool = True
    enable_ratio: bool = True

    # Matching behavior
    strict_missing: bool = True
    """Produce a ``MISSING`` violation when a reference key is absent from the text."""
    report_unexpected: bool = False
    """Treat numeric values without a reference counterpart as ``UNEXPECTED`` violations."""
    max_match_distance: int = 40
    """Proximity matching window, in characters."""
    fuzzy_cutoff: float = 0.8
    """Similarity threshold for fuzzy key matching (0.0 - 1.0)."""

    # Percentage comparison
    percent_as_fraction: bool = False
    """When ``True``, reference values are interpreted as fractions in 0-1 range (0.15)."""

    # Currency comparison
    exchange_rates: Mapping[str, float] = field(default_factory=dict)
    """Currency conversion rates. Key format: ``"EURUSD"`` (1 EUR = 1.10 USD)."""

    def __post_init__(self) -> None:
        errors: list[str] = []

        if self.atol < 0:
            errors.append("'atol' must not be negative")
        if self.rtol < 0:
            errors.append("'rtol' must not be negative")
        if self.rtol > self.max_rtol:
            errors.append(f"'rtol' must not exceed 'max_rtol' ({self.max_rtol})")
        if self.max_input_chars <= 0:
            errors.append("'max_input_chars' must be positive")
        if len(self.decimal_sep) != 1 or len(self.thousands_sep) != 1:
            errors.append("'decimal_sep' and 'thousands_sep' must be single characters")
        if self.decimal_sep == self.thousands_sep:
            errors.append("'decimal_sep' and 'thousands_sep' must differ")
        if not (0.0 <= self.fuzzy_cutoff <= 1.0):
            errors.append("'fuzzy_cutoff' must be within [0.0, 1.0]")
        if self.max_match_distance < 0:
            errors.append("'max_match_distance' must not be negative")
        if any(rate <= 0 for rate in self.exchange_rates.values()):
            errors.append("'exchange_rates' values must be positive")

        if errors:
            raise GuardConfigurationError("; ".join(errors))

    def is_extractor_enabled(self, name: str) -> bool:
        """Return whether the extractor with the given name is enabled."""
        flags = {
            "number": self.enable_number,
            "percentage": self.enable_percentage,
            "currency": self.enable_currency,
            "ratio": self.enable_ratio,
        }
        return flags.get(name, False)
