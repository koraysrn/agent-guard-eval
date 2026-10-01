"""Fuzzy key matcher using ``difflib`` for typo-tolerant key resolution."""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterable

from ..config import GuardConfig
from ..models import NumericMatch
from .base import Matcher


class FuzzyKeyMatcher(Matcher):
    """Resolves keys with minor typos via ``difflib.get_close_matches``."""

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
        tokens = re.findall(r"[A-Za-z]+", text)
        lowered_tokens = [token.lower() for token in tokens]
        result: dict[str, NumericMatch] = {}

        for key in key_list:
            close_matches = difflib.get_close_matches(
                key.lower(), lowered_tokens, n=1, cutoff=self.config.fuzzy_cutoff
            )
            if not close_matches:
                continue
            target = close_matches[0]
            for token_match in re.finditer(re.escape(target), text, re.IGNORECASE):
                nearest = min(
                    matches, key=lambda m: abs(m.start - token_match.start())
                )
                result[key] = nearest
        return result
