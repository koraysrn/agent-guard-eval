"""Extractor for percentage values in multiple notations."""

from __future__ import annotations

import re

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Extractor, SafeRegex, normalize_number


class PercentageExtractor(Extractor):
    """Extracts percentages such as ``15%``, ``15 %``, ``%15`` and ``percent 15``."""

    name = "percentage"

    def __init__(self, config: GuardConfig) -> None:
        super().__init__(config)
        self._patterns = [
            SafeRegex("percentage-trailing", self._trailing_pattern(config), config),
            SafeRegex("percentage-leading", self._leading_pattern(config), config),
            SafeRegex("percentage-word", self._word_pattern(config), config),
        ]

    @staticmethod
    def _number_part(config: GuardConfig) -> str:
        decimal = re.escape(config.decimal_sep)
        return rf"[+-]?\d+(?:{decimal}\d+)?"

    @classmethod
    def _trailing_pattern(cls, config: GuardConfig) -> str:
        return rf"({cls._number_part(config)})\s*%"

    @classmethod
    def _leading_pattern(cls, config: GuardConfig) -> str:
        return rf"%\s*({cls._number_part(config)})"

    @classmethod
    def _word_pattern(cls, config: GuardConfig) -> str:
        return rf"percent(?:age)?\s+({cls._number_part(config)})"

    def extract(self, text: str) -> list[NumericMatch]:
        matches: list[NumericMatch] = []
        for pattern in self._patterns:
            for match in pattern.finditer(text):
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
                        unit="%",
                    )
                )
        return matches
