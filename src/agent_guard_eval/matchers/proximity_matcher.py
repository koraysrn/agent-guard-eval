"""Proximity-based matcher: assigns the closest key within a character window."""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Matcher


class ProximityMatcher(Matcher):
    """Assigns the closest key to each match, bounded by ``max_match_distance``."""

    def __init__(self, config: GuardConfig) -> None:
        super().__init__(config)

    def match(
        self,
        text: str,
        matches: list[NumericMatch],
        keys: Iterable[str],
    ) -> dict[str, NumericMatch]:
        if not matches:
            return {}
        key_list = list(keys)
        positions: dict[str, list[int]] = {}
        for key in key_list:
            pattern = re.compile(
                r"(?<![A-Za-z0-9_])" + re.escape(key) + r"(?![A-Za-z0-9_])",
                re.IGNORECASE,
            )
            positions[key] = [m.start() for m in pattern.finditer(text)]

        result: dict[str, NumericMatch] = {}
        for match in matches:
            best_key: str | None = None
            best_distance = self.config.max_match_distance + 1
            for key in key_list:
                for position in positions[key]:
                    distance = abs(position - match.start)
                    if distance < best_distance:
                        best_key, best_distance = key, distance
            if best_key is not None:
                result[best_key] = match
        return result
