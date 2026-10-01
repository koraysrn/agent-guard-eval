"""Base machinery for key-to-value matchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from ..config import GuardConfig
from ..models import NumericMatch


class Matcher(ABC):
    """Base class for matchers that assign reference keys to extracted matches."""

    def __init__(self, config: GuardConfig) -> None:
        self.config = config

    @abstractmethod
    def match(
        self,
        text: str,
        matches: list[NumericMatch],
        keys: Iterable[str],
    ) -> dict[str, NumericMatch]:
        """Assign keys to matches and return ``{key: match}`` for every resolved key."""
        raise NotImplementedError
