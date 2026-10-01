"""Extractor for plain numbers: integers, decimals and scientific notation."""

from __future__ import annotations

import re

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Extractor, SafeRegex, normalize_number

# Currency symbols are owned by the dedicated currency extractor and therefore excluded
# from plain-number matching; the same applies to the percent sign.
_CURRENCY_SYMBOLS = "$€£¥₺"


class NumberExtractor(Extractor):
    """Extracts integers, grouped numbers, decimals and scientific notation."""

    name = "number"

    def __init__(self, config: GuardConfig) -> None:
        super().__init__(config)
        self._regex = SafeRegex(self.name, self._build_pattern(config), config)

    @staticmethod
    def _build_pattern(config: GuardConfig) -> str:
        thousands = re.escape(config.thousands_sep)
        decimal = re.escape(config.decimal_sep)
        symbols = _CURRENCY_SYMBOLS
        # The decimal separator is kept as a leading boundary to avoid matching the
        # fractional tail of a larger number ("12.5" must not yield a bare "5").
        # Comma is intentionally absent from both boundaries: it is legitimate
        # sentence punctuation after a number ("1.5, ..."), while grouped thousands
        # are already handled by the required 3-digit group quantifier.
        return (
            rf"(?<![\w{decimal}%{symbols}])"
            rf"([+-]?(?:\d{{1,3}}(?:{thousands}\d{{3}})+|\d+)"
            rf"(?:{decimal}\d+)?(?:[eE][+-]?\d+)?)"
            rf"(?![\w%{symbols}])"
        )

    def extract(self, text: str) -> list[NumericMatch]:
        matches: list[NumericMatch] = []
        for match in self._regex.finditer(text):
            raw = match.group(1)
            try:
                value = normalize_number(
                    raw, self.config.decimal_sep, self.config.thousands_sep
                )
            except ValueError:
                continue
            matches.append(
                NumericMatch(
                    key="",
                    value=value,
                    raw=raw,
                    start=match.start(1),
                    end=match.end(1),
                    source=self.name,
                )
            )
        return matches
