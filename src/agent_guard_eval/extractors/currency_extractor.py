"""Extractor for currency amounts expressed with symbols or ISO codes."""

from __future__ import annotations

import re

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Extractor, SafeRegex, normalize_number

_SYMBOL_TO_CODE: dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₺": "TRY",
}
_ISO_CODES = ("USD", "EUR", "GBP", "JPY", "TRY")


class CurrencyExtractor(Extractor):
    """Extracts currency amounts such as ``$1,234.56``, ``1.234,56 EUR`` or ``-₺99``."""

    name = "currency"

    def __init__(self, config: GuardConfig) -> None:
        super().__init__(config)
        self._specs = self._build_specs(config)

    @staticmethod
    def _amount_no_sign(config: GuardConfig) -> str:
        thousands = re.escape(config.thousands_sep)
        decimal = re.escape(config.decimal_sep)
        grouped = rf"\d{{1,3}}(?:{thousands}\d{{3}})+(?:{decimal}\d+)?"
        plain = rf"\d+(?:{decimal}\d+)?"
        return rf"(?:{grouped}|{plain})"

    @classmethod
    def _build_specs(
        cls, config: GuardConfig
    ) -> list[tuple[SafeRegex, int, int, int | None]]:
        amount = cls._amount_no_sign(config)
        symbol_class = rf"[{re.escape(''.join(_SYMBOL_TO_CODE))}]"
        iso_alternation = "|".join(_ISO_CODES)

        # (pattern, amount_group, unit_group, sign_group, flags)
        patterns: list[tuple[str, int, int, int | None, int]] = [
            (f"({symbol_class})\\s*([+-]?{amount})", 2, 1, None, 0),
            (f"([+-]?{amount})\\s*({symbol_class})", 1, 2, None, 0),
            (f"([+-])\\s*({symbol_class})\\s*({amount})", 3, 2, 1, 0),
            (rf"\b({iso_alternation})\s*([+-]?{amount})", 2, 1, None, re.IGNORECASE),
            (rf"([+-]?{amount})\s*({iso_alternation})\b", 1, 2, None, re.IGNORECASE),
        ]
        return [
            (
                SafeRegex(f"currency-{index}", pattern, config, flags),
                amount_group,
                unit_group,
                sign_group,
            )
            for index, (pattern, amount_group, unit_group, sign_group, flags) in enumerate(
                patterns
            )
        ]

    @staticmethod
    def _resolve_unit(token: str) -> str:
        if token in _SYMBOL_TO_CODE:
            return _SYMBOL_TO_CODE[token]
        return token.upper()

    def extract(self, text: str) -> list[NumericMatch]:
        matches: list[NumericMatch] = []
        for regex, amount_group, unit_group, sign_group in self._specs:
            for match in regex.finditer(text):
                raw = match.group(amount_group)
                sign = match.group(sign_group) if sign_group is not None else ""
                unit = self._resolve_unit(match.group(unit_group))
                try:
                    value = normalize_number(
                        sign + raw, self.config.decimal_sep, self.config.thousands_sep
                    )
                except ValueError:
                    continue
                matches.append(
                    NumericMatch(
                        key="",
                        value=value,
                        raw=sign + raw,
                        start=match.start(),
                        end=match.end(),
                        source=self.name,
                        unit=unit,
                    )
                )
        return self._dedupe(matches)

    @staticmethod
    def _dedupe(matches: list[NumericMatch]) -> list[NumericMatch]:
        """Drop nested duplicates (e.g. ``-$5.00`` also matched as ``$5.00``)."""
        if not matches:
            return matches
        ordered = sorted(matches, key=lambda m: (m.start, -(m.end - m.start)))
        kept: list[NumericMatch] = []
        for candidate in ordered:
            overlaps = any(
                candidate.start < existing.end and existing.start < candidate.end
                for existing in kept
            )
            if not overlaps:
                kept.append(candidate)
        kept.sort(key=lambda m: m.start)
        return kept
