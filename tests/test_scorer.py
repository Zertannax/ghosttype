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
    """Test exit codes match SCORE_LABELS buckets at boundaries."""
    # Clean / Mild → 0
    assert _get_exit_code(0) == EXIT_CLEAN
    assert _get_exit_code(30) == EXIT_CLEAN
    assert _get_exit_code(40) == EXIT_CLEAN
    # Moderate → 1
    assert _get_exit_code(41) == EXIT_MODERATE
    assert _get_exit_code(50) == EXIT_MODERATE
    assert _get_exit_code(60) == EXIT_MODERATE
    # High / Critical → 2
    assert _get_exit_code(61) == EXIT_HIGH
    assert _get_exit_code(80) == EXIT_HIGH
    assert _get_exit_code(100) == EXIT_HIGH


def test_get_label_boundaries() -> None:
    """Labels at every bucket boundary."""
    assert _get_label(0) == "Clean"
    assert _get_label(20) == "Clean"
    assert _get_label(21) == "Mild"
    assert _get_label(40) == "Mild"
    assert _get_label(41) == "Moderate"
    assert _get_label(60) == "Moderate"
    assert _get_label(61) == "High"
    assert _get_label(80) == "High"
    assert _get_label(81) == "Critical"
    assert _get_label(100) == "Critical"


def test_score_passage_no_hits() -> None:
    """Test passage with no hits scores 0 with no rule flags."""
    passage = Passage(index=0, text="Clean text.", start_char=0, end_char=11)
    score, cluster, bz05 = _score_passage(passage, [])
    assert score == 0
    assert cluster is False
    assert bz05 is False


def test_score_passage_with_hits() -> None:
    """Short passage with two strong hits hits the 100 ceiling."""
    passage = Passage(index=0, text="In today's world, we must leverage synergy.", start_char=0, end_char=43)
    hits = [
        PatternHit(pattern_id="OP-01", category="opener", matched_text="In today's world", start_char=0, end_char=17, severity=0.8),
        PatternHit(pattern_id="BZ-01", category="buzzword", matched_text="synergy", start_char=35, end_char=42, severity=0.6),
    ]
    score, _cluster, _bz05 = _score_passage(passage, hits)
    # 8 words → floored to 10 ; sqrt(10)/3 ≈ 1.054 ; (1.4 / 1.054) * 100 ≈ 133 → clamped 100
    assert score == 100


def test_score_passage_low_severity_short_text() -> None:
    """Single low-severity hit on short text produces a moderate (not high) score."""
    passage = Passage(index=0, text="It is worth noting this fact.", start_char=0, end_char=29)
    hits = [
        PatternHit(pattern_id="HE-01", category="hedge", matched_text="It is worth noting", start_char=0, end_char=18, severity=0.5),
    ]
    score, _cluster, _bz05 = _score_passage(passage, hits)
    # 6 words → floored to 10 ; sqrt(10)/3 ≈ 1.054 ; (0.5 / 1.054) * 100 ≈ 47
    assert 40 <= score <= 55, f"Expected score in [40, 55], got {score}"


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
    # Heuristic-only path (no semantic / stylistic) — first passage hits the ceiling,
    # second is empty. Length-weighted average puts the doc score above Clean.
    assert result.score >= 50, f"Doc score {result.score} too low for known slop"
    assert result.label in ("Moderate", "High", "Critical")
    assert result.total_hits == 2
    assert len(result.passages) == 2
    assert result.passages[0].score == 100
    assert result.passages[1].score == 0


def test_aggregate_human_indicator_bonus_applied() -> None:
    """Negative-severity hits (human indicators) reduce the document score."""
    passage = Passage(index=0, text="A quote from a great speaker, classical and human.", start_char=0, end_char=51)
    hits_with_oratory = {
        0: [
            PatternHit(pattern_id="OP-01", category="opener", matched_text="A quote", start_char=0, end_char=7, severity=0.8),
            PatternHit(pattern_id="JR-21", category="oratory", matched_text="classical", start_char=30, end_char=39, severity=-0.5),
            PatternHit(pattern_id="JR-22", category="oratory", matched_text="human", start_char=45, end_char=50, severity=-0.5),
            PatternHit(pattern_id="JR-23", category="oratory", matched_text="speaker", start_char=14, end_char=21, severity=-0.5),
        ],
    }
    hits_no_oratory = {
        0: [
            PatternHit(pattern_id="OP-01", category="opener", matched_text="A quote", start_char=0, end_char=7, severity=0.8),
        ],
    }
    r_with = aggregate([passage], hits_with_oratory)
    r_without = aggregate([passage], hits_no_oratory)
    assert r_with.score < r_without.score, (
        f"Human-indicator bonus did not lower score: with={r_with.score}, without={r_without.score}"
    )


def test_aggregate_no_semantic_falls_back_cleanly() -> None:
    """semantic_score=None and stylistic_score=None must not crash."""
    passage = Passage(index=0, text="Plain text.", start_char=0, end_char=11)
    result = aggregate([passage], {0: []}, semantic_score=None, stylistic_score=None)
    assert result.score == 0
    assert result.label == "Clean"
    assert result.exit_code == EXIT_CLEAN


# ---------- clustering bonus + BZ-05 rule (PATTERNS.md spec) ----------

def test_cluster_bonus_three_categories_amplifies_score() -> None:
    """3+ distinct categories → +15% multiplier on the raw score."""
    text = "Some moderately long passage text here with multiple words for normalisation."
    passage = Passage(index=0, text=text, start_char=0, end_char=len(text))
    # Two-category baseline
    two_cats = [
        PatternHit(pattern_id="OP-01", category="opener", matched_text="x", start_char=0, end_char=1, severity=0.4),
        PatternHit(pattern_id="HE-01", category="hedge", matched_text="y", start_char=2, end_char=3, severity=0.4),
    ]
    # Three-category cluster
    three_cats = two_cats + [
        PatternHit(pattern_id="BZ-01", category="buzzword", matched_text="z", start_char=4, end_char=5, severity=0.4),
    ]
    score_2, cluster_2, _ = _score_passage(passage, two_cats)
    score_3, cluster_3, _ = _score_passage(passage, three_cats)
    # Adding one more hit should bump the score; the cluster multiplier amplifies
    # it further than the linear severity addition alone would.
    assert score_3 > score_2
    assert cluster_2 is False
    assert cluster_3 is True


def test_cluster_bonus_ignores_negative_severity_categories() -> None:
    """Human-indicator (negative severity) categories don't count toward cluster."""
    text = "A short passage with a few words inside it for the test."
    passage = Passage(index=0, text=text, start_char=0, end_char=len(text))
    hits_two_pos_one_neg = [
        PatternHit(pattern_id="OP-01", category="opener", matched_text="a", start_char=0, end_char=1, severity=0.4),
        PatternHit(pattern_id="HE-01", category="hedge", matched_text="b", start_char=2, end_char=3, severity=0.4),
        PatternHit(pattern_id="JR-21", category="classical_oratory", matched_text="c", start_char=4, end_char=5, severity=-0.4),
    ]
    hits_three_pos = [
        PatternHit(pattern_id="OP-01", category="opener", matched_text="a", start_char=0, end_char=1, severity=0.4),
        PatternHit(pattern_id="HE-01", category="hedge", matched_text="b", start_char=2, end_char=3, severity=0.4),
        PatternHit(pattern_id="BZ-01", category="buzzword", matched_text="c", start_char=4, end_char=5, severity=0.4),
    ]
    s_with_neg, cluster_neg, _ = _score_passage(passage, hits_two_pos_one_neg)
    s_three_pos, cluster_pos, _ = _score_passage(passage, hits_three_pos)
    # 3 positive categories triggers cluster bonus; 2 positive + 1 negative does not.
    assert s_three_pos > s_with_neg
    assert cluster_neg is False
    assert cluster_pos is True


def test_bz05_special_rule_two_tells_force_high() -> None:
    """2+ BZ-05 hits in a passage floor the score to >= 70 (HIGH)."""
    text = "We delve into the multifaceted nature of the topic with care."
    passage = Passage(index=0, text=text, start_char=0, end_char=len(text))
    hits = [
        PatternHit(pattern_id="BZ-05", category="buzzword", matched_text="delve", start_char=3, end_char=8, severity=0.9),
        PatternHit(pattern_id="BZ-05", category="buzzword", matched_text="multifaceted", start_char=20, end_char=32, severity=0.9),
    ]
    score, _cluster, bz05 = _score_passage(passage, hits)
    assert score >= 70, f"BZ-05 rule: expected score >= 70, got {score}"
    assert bz05 is True


def test_bz05_special_rule_one_tell_does_not_trigger() -> None:
    """A single BZ-05 hit should NOT trigger the HIGH floor."""
    long_text = " ".join(["padding"] * 60) + " multifaceted approach is needed."
    passage = Passage(index=0, text=long_text, start_char=0, end_char=len(long_text))
    hits = [
        PatternHit(pattern_id="BZ-05", category="buzzword", matched_text="multifaceted",
                   start_char=long_text.find("multifaceted"),
                   end_char=long_text.find("multifaceted") + 12, severity=0.9),
    ]
    score, _cluster, bz05 = _score_passage(passage, hits)
    # Long passage + single hit + no cluster → well below 70
    assert score < 70, f"Single BZ-05 hit should not trigger HIGH floor, got {score}"
    assert bz05 is False
