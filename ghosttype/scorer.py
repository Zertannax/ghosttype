"""Score aggregation and labeling."""

import math
from dataclasses import dataclass

from ghosttype.heuristics.engine import PatternHit
from ghosttype.preprocessor import Passage

# Three-way mix weights when both semantic and stylistic are available.
HEURISTIC_WEIGHT = 0.40
SEMANTIC_WEIGHT = 0.30
STYLISTIC_WEIGHT = 0.30

# Two-way mix weights (legacy fallback when stylistic is missing).
HEURISTIC_WEIGHT_2WAY = 0.55
SEMANTIC_WEIGHT_2WAY = 0.45

# Cluster bonus per PATTERNS.md: 3+ distinct categories in one passage are more
# diagnostic than the same number of hits in a single category.
CLUSTER_CATEGORY_THRESHOLD = 3
CLUSTER_BONUS_MULTIPLIER = 1.15

# BZ-05 special rule per PATTERNS.md: 2+ high-confidence AI tells in one passage
# (delve, tapestry, nuanced understanding, multifaceted) force the passage HIGH.
BZ05_RULE_MIN_HITS = 2
BZ05_RULE_MIN_SCORE = 70


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
    """Get exit code for a score, aligned with SCORE_LABELS buckets.

    0 = Clean/Mild (score <= 40)
    1 = Moderate (41 <= score <= 60)
    2 = High/Critical (score >= 61)
    """
    if score <= 40:
        return EXIT_CLEAN
    if score <= 60:
        return EXIT_MODERATE
    return EXIT_HIGH


def _score_passage(passage: Passage, hits: list[PatternHit]) -> int:
    """Calculate score for a single passage.

    Formula: sum of severities normalized by passage word count, then:
    - Multiply by CLUSTER_BONUS_MULTIPLIER when 3+ distinct categories appear
      together (cluster effect from PATTERNS.md).
    - Floor at BZ05_RULE_MIN_SCORE when 2+ BZ-05 high-confidence tells appear
      (delve / tapestry / nuanced understanding / multifaceted).
    """
    if not hits:
        return 0

    total_severity = sum(hit.severity for hit in hits)
    # Normalize by word count (was character count — penalised short passages
    # disproportionately). Floor at 10 words to keep tiny passages from
    # producing crushing per-hit scores.
    word_count = max(10, len(passage.text.split()))
    length_factor = math.sqrt(word_count) / 3.0
    raw_score = (total_severity / length_factor) * 100

    # Cluster bonus: 3+ distinct positive-severity categories in the same passage.
    distinct_categories = {h.category for h in hits if h.severity > 0}
    if len(distinct_categories) >= CLUSTER_CATEGORY_THRESHOLD:
        raw_score *= CLUSTER_BONUS_MULTIPLIER

    score = min(100, max(0, round(raw_score)))

    # BZ-05 special rule: 2+ high-confidence AI tells force the passage HIGH.
    bz05_count = sum(1 for h in hits if h.pattern_id == "BZ-05")
    if bz05_count >= BZ05_RULE_MIN_HITS:
        score = max(score, BZ05_RULE_MIN_SCORE)

    return score


def aggregate(
    passages: list[Passage],
    hits_by_passage: dict[int, list[PatternHit]],
    semantic_score: float | None = None,
    stylistic_score: float | None = None,
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

    # Detect strong human indicators (negative severity patterns)
    human_indicators = sum(
        1 for passage in passages
        for hit in hits_by_passage.get(passage.index, [])
        if hit.severity < 0
    )

    # Adjust weights: more human indicators = trust semantic/stylistic less
    if human_indicators >= 3:
        # Strong human text detected (classical oratory, etc.)
        h_weight, s_weight, st_weight = 0.30, 0.35, 0.35
        # Apply human bonus
        human_bonus = -5 * min(human_indicators, 10)  # Cap at -50
    elif human_indicators >= 1:
        h_weight, s_weight, st_weight = 0.35, 0.325, 0.325
        human_bonus = -3 * human_indicators
    else:
        h_weight, s_weight, st_weight = HEURISTIC_WEIGHT, SEMANTIC_WEIGHT, STYLISTIC_WEIGHT
        human_bonus = 0

    # Combine scores
    if semantic_score is not None and stylistic_score is not None:
        combined = (
            h_weight * heuristic_score +
            s_weight * (semantic_score * 100) +
            st_weight * (stylistic_score * 100) +
            human_bonus
        )
        doc_score = round(combined)
    elif semantic_score is not None:
        combined = HEURISTIC_WEIGHT_2WAY * heuristic_score + SEMANTIC_WEIGHT_2WAY * (semantic_score * 100)
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
