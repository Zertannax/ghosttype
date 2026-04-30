"""Score aggregation and labeling."""

import math
from dataclasses import dataclass

from ghosttype.heuristics.engine import PatternHit
from ghosttype.preprocessor import Passage

# Score weights
SEMANTIC_WEIGHT = 0.45
HEURISTIC_WEIGHT = 0.55


@dataclass
class PassageResult:
    """Scoring result for a single passage."""

    passage: Passage
    score: int
    hits: list[PatternHit]
    label: str


@dataclass
class AnalysisResult:
    """Complete analysis result for a document."""

    score: int
    label: str
    passages: list[PassageResult]
    total_hits: int
    exit_code: int


# Score ranges and labels
SCORE_LABELS = [
    (0, 20, "Clean"),
    (21, 40, "Mild"),
    (41, 60, "Moderate"),
    (61, 80, "High"),
    (81, 100, "Critical"),
]

# Exit code thresholds
EXIT_CLEAN = 0
EXIT_MODERATE = 1
EXIT_HIGH = 2


def _get_label(score: int) -> str:
    """Get label for a score."""
    for min_score, max_score, label in SCORE_LABELS:
        if min_score <= score <= max_score:
            return label
    return "Unknown"


def _get_exit_code(score: int) -> int:
    """Get exit code for a score."""
    if score < 40:
        return EXIT_CLEAN
    if score <= 70:
        return EXIT_MODERATE
    return EXIT_HIGH


def _score_passage(passage: Passage, hits: list[PatternHit]) -> int:
    """Calculate score for a single passage.

    Formula: sum of severities normalized by passage length.
    """
    if not hits:
        return 0

    total_severity = sum(hit.severity for hit in hits)
    # Normalize: longer passages need more hits for same score
    length_factor = math.sqrt(max(50, len(passage.text))) / 10
    raw_score = (total_severity / length_factor) * 100

    return min(100, max(0, round(raw_score)))


def aggregate(
    passages: list[Passage],
    hits_by_passage: dict[int, list[PatternHit]],
    semantic_score: float | None = None,
) -> AnalysisResult:
    """Aggregate passage scores into document score.

    Args:
        passages: List of preprocessed passages.
        hits_by_passage: Dictionary mapping passage index to hits.
        semantic_score: Optional semantic score 0.0-1.0.

    Returns:
        AnalysisResult with overall score and labels.
    """
    passage_results: list[PassageResult] = []
    total_weighted_score = 0.0
    total_length = 0
    total_hits = 0

    for passage in passages:
        hits = hits_by_passage.get(passage.index, [])
        passage_score = _score_passage(passage, hits)
        label = _get_label(passage_score)

        passage_results.append(
            PassageResult(
                passage=passage,
                score=passage_score,
                hits=hits,
                label=label,
            )
        )

        # Weight by passage length
        weight = len(passage.text)
        total_weighted_score += passage_score * weight
        total_length += weight
        total_hits += len(hits)

    # Heuristic document score
    heuristic_score = total_weighted_score / total_length if total_length > 0 else 0

    # Combine with semantic score if available
    if semantic_score is not None:
        combined = HEURISTIC_WEIGHT * heuristic_score + SEMANTIC_WEIGHT * (semantic_score * 100)
        doc_score = round(combined)
    else:
        doc_score = round(heuristic_score)

    doc_score = min(100, max(0, doc_score))
    doc_label = _get_label(doc_score)
    exit_code = _get_exit_code(doc_score)

    return AnalysisResult(
        score=doc_score,
        label=doc_label,
        passages=passage_results,
        total_hits=total_hits,
        exit_code=exit_code,
    )
