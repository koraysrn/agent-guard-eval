"""Core validation orchestration.

The :class:`NumericGuard` runs the full pipeline: extract numeric values, match them
against reference keys, compare them with the tolerance formula, and emit a structured
:class:`ValidationResult`. No LLM is involved anywhere in the flow.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from .comparators.currency_comparator import CurrencyComparator
from .comparators.numeric_comparator import NumericComparator
from .comparators.percentage_comparator import PercentageComparator
from .config import GuardConfig
from .exceptions import GuardInputError
from .extractors.base import Extractor
from .extractors.currency_extractor import CurrencyExtractor
from .extractors.number_extractor import NumberExtractor
from .extractors.percentage_extractor import PercentageExtractor
from .extractors.ratio_extractor import RatioExtractor
from .logging import get_logger
from .matchers.base import Matcher
from .matchers.fuzzy_key_matcher import FuzzyKeyMatcher
from .matchers.label_matcher import LabelMatcher
from .matchers.proximity_matcher import ProximityMatcher
from .models import DiffDetail, GuardViolation, NumericMatch, ValidationResult
from .report.diff import (
    build_mismatch_violation,
    build_missing_violation,
    build_unexpected_violation,
)

# Higher priority wins when two matches overlap; specialized extractors own their spans.
_PRIORITY: dict[str, int] = {"currency": 3, "percentage": 2, "ratio": 1, "number": 0}


class NumericGuard:
    """Deterministic guard that validates numeric values in text against ground truth."""

    def __init__(
        self,
        ground_truth: Mapping[str, float],
        config: GuardConfig | None = None,
        units: Mapping[str, str] | None = None,
    ) -> None:
        self.ground_truth = dict(ground_truth)
        self.config = config or GuardConfig()
        self.units = dict(units or {})
        self._logger = get_logger("agent_guard_eval.guard")
        self._extractors = self._build_extractors()
        self._matchers = self._build_matchers()

    def _build_extractors(self) -> list[Extractor]:
        extractors: list[Extractor] = []
        if self.config.enable_currency:
            extractors.append(CurrencyExtractor(self.config))
        if self.config.enable_percentage:
            extractors.append(PercentageExtractor(self.config))
        if self.config.enable_ratio:
            extractors.append(RatioExtractor(self.config))
        if self.config.enable_number:
            extractors.append(NumberExtractor(self.config))
        return extractors

    def _build_matchers(self) -> list[Matcher]:
        return [
            LabelMatcher(self.config),
            ProximityMatcher(self.config),
            FuzzyKeyMatcher(self.config),
        ]

    def validate(self, text: str) -> ValidationResult:
        """Validate ``text`` against the configured ground truth and return the result."""
        self._validate_input(text)

        matches = self._extract(text)
        matches = self._deduplicate(matches)
        matched = self._match(text, matches)
        diffs, violations = self._compare(matched)

        if self.config.report_unexpected:
            violations.extend(self._unexpected_violations(matches, matched))

        is_valid = not violations
        details = {
            "matches": [match.to_dict() for match in matches],
            "matched_keys": sorted(matched),
            "diffs": [diff.to_dict() for diff in diffs],
        }
        self._logger.debug("Validated %d chars; %d violations", len(text), len(violations))
        return ValidationResult(
            is_valid=is_valid,
            violations=tuple(violations),
            details=details,
            text_length=len(text),
            extracted_count=len(matches),
        )

    def _validate_input(self, text: str) -> None:
        if not isinstance(text, str):
            raise GuardInputError("Input text must be a string")
        if len(text) > self.config.max_input_chars:
            raise GuardInputError(
                f"Input of {len(text)} chars exceeds max_input_chars "
                f"({self.config.max_input_chars})"
            )

    def _extract(self, text: str) -> list[NumericMatch]:
        matches: list[NumericMatch] = []
        for extractor in self._extractors:
            matches.extend(extractor.extract(text))
        return matches

    @staticmethod
    def _deduplicate(matches: list[NumericMatch]) -> list[NumericMatch]:
        """Remove lower-priority matches that overlap higher-priority ones."""
        if not matches:
            return matches
        ordered = sorted(
            matches, key=lambda m: (-_PRIORITY.get(m.source, 0), m.start)
        )
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

    def _match(
        self, text: str, matches: list[NumericMatch]
    ) -> dict[str, NumericMatch]:
        if not matches:
            return {}
        keys = list(self.ground_truth)
        resolved: dict[str, NumericMatch] = {}
        for matcher in self._matchers:
            for key, match in matcher.match(text, matches, keys).items():
                resolved.setdefault(key, match)
        return {key: replace(match, key=key) for key, match in resolved.items()}

    def _compare(
        self, matched: dict[str, NumericMatch]
    ) -> tuple[list[DiffDetail], list[GuardViolation]]:
        diffs: list[DiffDetail] = []
        violations: list[GuardViolation] = []
        for key, expected in self.ground_truth.items():
            match = matched.get(key)
            unit = self.units.get(key, "")
            if not unit and match is not None:
                unit = match.unit

            if match is None:
                if self.config.strict_missing:
                    violations.append(build_missing_violation(key, expected, unit))
                continue

            comparator = self._select_comparator(unit, match)
            diff = comparator.compare(key, match, expected, unit)
            diffs.append(diff)
            if not diff.passed:
                violations.append(build_mismatch_violation(diff))
        return diffs, violations

    def _unexpected_violations(
        self,
        matches: list[NumericMatch],
        matched: dict[str, NumericMatch],
    ) -> list[GuardViolation]:
        """Report extracted values that were never assigned to a reference key."""
        used_spans = {match.span() for match in matched.values()}
        return [
            build_unexpected_violation(replace(match, key=match.raw))
            for match in matches
            if match.span() not in used_spans
        ]

    def _select_comparator(
        self, unit: str, match: NumericMatch
    ) -> NumericComparator | PercentageComparator | CurrencyComparator:
        """Pick the comparator appropriate for the key's unit and match source."""
        if unit == "percent" or match.source == "percentage":
            return PercentageComparator(self.config)
        if match.source == "currency" or (unit and len(unit) == 3 and unit.isupper()):
            return CurrencyComparator(self.config)
        return NumericComparator(self.config)
