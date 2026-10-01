"""Label-based matcher: resolves keys written as explicit ``key:`` or ``key =`` labels."""

from __future__ import annotations

import re
from collections.abc import Iterable

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Matcher


class LabelMatcher(Matcher):
    """Matches keys that appear as labels, e.g. ``Sharpe: 1.5`` or ``Variance = 2.1``."""

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
        result: dict[str, NumericMatch] = {}
        for key in keys:
            label_match = re.search(re.escape(key) + r"\s*[:=]\s*", text, re.IGNORECASE)
            if not label_match:
                continue
            nearest = self._nearest_after(matches, label_match.end())
            if nearest is not None:
                result[key] = nearest
        return result

    @staticmethod
    def _nearest_after(
        matches: list[NumericMatch], position: int
    ) -> NumericMatch | None:
        """Return the match with the smallest start position at or after ``position``."""
        best: NumericMatch | None = None
        best_distance: int | None = None
        for match in matches:
            if match.start < position:
                continue
            distance = match.start - position
            if best_distance is None or distance < best_distance:
                best, best_distance = match, distance
        return best
