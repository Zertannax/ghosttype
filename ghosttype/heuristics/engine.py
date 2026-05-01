"""Heuristic detection engine."""

import re
from dataclasses import dataclass
from typing import Any

from ghosttype.heuristics.patterns import ALL_PATTERNS
from ghosttype.preprocessor import Passage


@dataclass
class PatternHit:
    """A detected pattern match."""

    pattern_id: str
    category: str
    matched_text: str
    start_char: int
    end_char: int
    severity: float


class PatternDefinition:
    """Definition of a detection pattern."""

    def __init__(
        self,
        pattern_id: str,
        category: str,
        regex: str,
        severity: float,
        description: str = "",
    ):
        self.pattern_id = pattern_id
        self.category = category
        self.regex = re.compile(regex, re.IGNORECASE | re.MULTILINE)
        self.severity = severity
        self.description = description

    def detect(self, text: str, passage_offset: int = 0) -> list[PatternHit]:
        """Detect all occurrences of this pattern in text."""
        hits: list[PatternHit] = []
        for match in self.regex.finditer(text):
            hits.append(
                PatternHit(
                    pattern_id=self.pattern_id,
                    category=self.category,
                    matched_text=match.group(),
                    start_char=passage_offset + match.start(),
                    end_char=passage_offset + match.end(),
                    severity=self.severity,
                )
            )
        return hits


class HeuristicEngine:
    """Orchestrates all pattern detectors."""

    def __init__(self) -> None:
        self.patterns: list[PatternDefinition] = []
        for p in ALL_PATTERNS:
            p_any: Any = p
            self.patterns.append(
                PatternDefinition(
                    pattern_id=p_any["id"],
                    category=p_any["category"],
                    regex=p_any["regex"],
                    severity=p_any["severity"],
                    description=p_any.get("description", ""),
                )
            )

    def analyze(self, passages: list[Passage]) -> dict[int, list[PatternHit]]:
        """Analyze passages and return hits per passage index.

        Hits sharing the same (matched_text lowercased, start_char) are deduplicated:
        a single phrase like "in summary" listed in three categories must not be
        counted three times by the scorer.

        Args:
            passages: List of preprocessed passages.

        Returns:
            Dictionary mapping passage index to list of hits.
        """
        results: dict[int, list[PatternHit]] = {}

        for passage in passages:
            hits: list[PatternHit] = []
            for pattern in self.patterns:
                pattern_hits = pattern.detect(passage.text, passage.start_char)
                hits.extend(pattern_hits)
            results[passage.index] = self._dedupe_hits(hits)

        return results

    @staticmethod
    def _dedupe_hits(hits: list[PatternHit]) -> list[PatternHit]:
        """Drop overlapping hits at the same starting position; keep strongest signal.

        Two hits "overlap" when they start at the same character. The same phrase
        ("in summary", "it is important") often appears in 3-4 pattern categories
        with slightly different trailing punctuation — this collapses them into one.

        Strongest = largest absolute severity. Negative severities (human indicators)
        are preserved when they outrank positive duplicates at the same span.
        """
        best: dict[int, PatternHit] = {}
        for hit in hits:
            current = best.get(hit.start_char)
            if current is None or abs(hit.severity) > abs(current.severity):
                best[hit.start_char] = hit
        return list(best.values())

    def get_categories(self) -> set[str]:
        """Return all unique category names."""
        return {p.category for p in self.patterns}
