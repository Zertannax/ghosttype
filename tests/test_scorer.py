"""Tests for score aggregator."""

from ghosttype.heuristics.engine import PatternHit
from ghosttype.preprocessor import Passage
from ghosttype.scorer import (
    EXIT_CLEAN,
    EXIT_HIGH,
    EXIT_MODERATE,
    AnalysisResult,
    _get_exit_code,
    _get_label,
    _score_passage,
    aggregate,
)


def test_get_label_clean() -> None:
    """Test Clean label."""
    assert _get_label(10) == "Clean"
    assert _get_label(20) == "Clean"


def test_get_label_moderate() -> None:
    """Test Moderate label."""
    assert _get_label(50) == "Moderate"


def test_get_label_critical() -> None:
    """Test Critical label."""
    assert _get_label(90) == "Critical"


def test_get_exit_code() -> None:
    """Test exit codes."""
    assert _get_exit_code(30) == EXIT_CLEAN
    assert _get_exit_code(50) == EXIT_MODERATE
    assert _get_exit_code(80) == EXIT_HIGH


def test_score_passage_no_hits() -> None:
    """Test passage with no hits scores 0."""
    passage = Passage(index=0, text="Clean text.", start_char=0, end_char=11)
    assert _score_passage(passage, []) == 0


def test_score_passage_with_hits() -> None:
    """Test passage with hits scores above 0."""
    passage = Passage(index=0, text="In today's world, we must leverage synergy.", start_char=0, end_char=43)
    hits = [
        PatternHit(pattern_id="OP-01", category="opener", matched_text="In today's world", start_char=0, end_char=17, severity=0.8),
        PatternHit(pattern_id="BZ-01", category="buzzword", matched_text="synergy", start_char=35, end_char=42, severity=0.6),
    ]
    score = _score_passage(passage, hits)
    assert score > 0
    assert score <= 100


def test_aggregate_empty() -> None:
    """Test aggregation with empty input."""
    result = aggregate([], {})
    assert result.score == 0
    assert result.label == "Clean"
    assert result.exit_code == EXIT_CLEAN
    assert result.total_hits == 0


def test_aggregate_with_passages() -> None:
    """Test aggregation with passages and hits."""
    passages = [
        Passage(index=0, text="In today's world, we must leverage synergy.", start_char=0, end_char=43),
        Passage(index=1, text="The cat sat on the mat.", start_char=44, end_char=67),
    ]
    hits = {
        0: [
            PatternHit(pattern_id="OP-01", category="opener", matched_text="In today's world", start_char=0, end_char=17, severity=0.8),
            PatternHit(pattern_id="BZ-01", category="buzzword", matched_text="synergy", start_char=35, end_char=42, severity=0.6),
        ],
        1: [],
    }

    result = aggregate(passages, hits)
    assert isinstance(result, AnalysisResult)
    assert result.score >= 0
    assert result.score <= 100
    assert result.total_hits == 2
    assert len(result.passages) == 2
