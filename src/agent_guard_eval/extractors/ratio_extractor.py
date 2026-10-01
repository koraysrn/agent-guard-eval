"""Extractor for ratios such as ``3:1`` and ``3/4``."""

from __future__ import annotations

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Extractor, SafeRegex


class RatioExtractor(Extractor):
    """Extracts ratios in ``a:b`` and ``a/b`` notation as their decimal value."""

    name = "ratio"

    def __init__(self, config: GuardConfig) -> None:
        super().__init__(config)
        self._colon = SafeRegex("ratio-colon", r"(\d+)\s*:\s*(\d+)", config)
        # Date-like sequences such as "3/4/2024" are rejected via the lookarounds.
        self._slash = SafeRegex("ratio-slash", r"(?<![\d/])(\d+)\s*/\s*(\d+)(?![\d/])", config)

    def extract(self, text: str) -> list[NumericMatch]:
        matches: list[NumericMatch] = []
        for regex in (self._colon, self._slash):
            for match in regex.finditer(text):
                try:
                    numerator = int(match.group(1))
                    denominator = int(match.group(2))
                except ValueError:
                    continue
                if denominator == 0:
                    continue
                raw = match.group(0)
                matches.append(
                    NumericMatch(
                        key="",
                        value=numerator / denominator,
                        raw=raw,
                        start=match.start(),
                        end=match.end(),
                        source=self.name,
                        unit="ratio",
                    )
                )
        return matches
