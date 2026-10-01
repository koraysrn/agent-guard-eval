"""Base machinery for numeric extractors.

Extractors rely on pre-compiled, backtracking-free regular expressions and an input
size guard. Combined with the ``max_input_chars`` limit, this mitigates ReDoS and DoS
vectors without depending on a third-party regex engine.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from re import Match, Pattern

from ..config import GuardConfig
from ..exceptions import GuardExtractionError
from ..models import NumericMatch


def compile_pattern(name: str, pattern: str, flags: int = 0) -> Pattern[str]:
    """Compile ``pattern``, raising :class:`GuardExtractionError` on failure."""
    try:
        return re.compile(pattern, flags)
    except re.error as exc:
        raise GuardExtractionError(f"Invalid regex pattern '{name}': {exc}") from exc


def normalize_number(raw: str, decimal_sep: str, thousands_sep: str) -> float:
    """Convert a locale-formatted numeric string into a ``float``."""
    text = raw.strip()
    sign = ""
    if text and text[0] in "+-":
        sign, text = text[0], text[1:]
    if thousands_sep:
        text = text.replace(thousands_sep, "")
    if decimal_sep != ".":
        text = text.replace(decimal_sep, ".")
    return float(sign + text)


class SafeRegex:
    """A compiled pattern with an input-size guard.

    Python's ``re`` module has no built-in timeout, so ReDoS is prevented structurally:
    extractor patterns avoid nested quantifiers (catastrophic backtracking) and every
    search is bounded by ``max_input_chars``.
    """

    def __init__(self, name: str, pattern: str, config: GuardConfig, flags: int = 0) -> None:
        self.name = name
        self.config = config
        self.pattern = compile_pattern(name, pattern, flags)

    def _check_size(self, text: str) -> None:
        if len(text) > self.config.max_input_chars:
            raise GuardExtractionError(
                f"Input of {len(text)} chars exceeds max_input_chars "
                f"({self.config.max_input_chars})"
            )

    def finditer(self, text: str) -> Iterator[Match[str]]:
        """Yield matches, enforcing the input-size guard first."""
        self._check_size(text)
        return self.pattern.finditer(text)

    def search(self, text: str) -> Match[str] | None:
        """Return the first match, enforcing the input-size guard first."""
        self._check_size(text)
        return self.pattern.search(text)


class Extractor(ABC):
    """Base class for all numeric extractors."""

    name: str = "base"

    def __init__(self, config: GuardConfig) -> None:
        self.config = config

    @abstractmethod
    def extract(self, text: str) -> list[NumericMatch]:
        """Extract every numeric match of this extractor's kind from ``text``."""
        raise NotImplementedError
