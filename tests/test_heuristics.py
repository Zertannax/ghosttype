"""Tests for heuristic engine."""

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import Passage


def test_engine_detects_opener() -> None:
    """Test detection of generic opener."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="In today's fast-paced world, we must adapt.", start_char=0, end_char=42)]
    results = engine.analyze(passages)

    assert 0 in results
    assert len(results[0]) > 0
    assert any(h.pattern_id == "OP-01" for h in results[0])


def test_engine_detects_hedge() -> None:
    """Test detection of hedge filler."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="It is worth noting that this works.", start_char=0, end_char=35)]
    results = engine.analyze(passages)

    assert any(h.pattern_id == "HE-01" for h in results[0])


def test_engine_detects_buzzword() -> None:
    """Test detection of buzzword."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="This is a comprehensive approach.", start_char=0, end_char=33)]
    results = engine.analyze(passages)

    assert any(h.pattern_id == "BZ-02" for h in results[0])


def test_engine_high_severity_buzzword() -> None:
    """Test high severity AI buzzwords."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="Let me delve into this nuanced understanding.", start_char=0, end_char=45)]
    results = engine.analyze(passages)

    hits = results[0]
    bz05_hits = [h for h in hits if h.pattern_id == "BZ-05"]
    assert len(bz05_hits) > 0
    assert bz05_hits[0].severity == 0.9


def test_engine_no_false_positives() -> None:
    """Test that normal text produces no hits."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="The cat sat on the mat. It was sunny outside.", start_char=0, end_char=46)]
    results = engine.analyze(passages)

    assert len(results[0]) == 0


def test_engine_multiple_patterns() -> None:
    """Test detection of multiple patterns in one passage."""
    engine = HeuristicEngine()
    text = "In today's world, we must leverage our synergy."
    passages = [Passage(index=0, text=text, start_char=0, end_char=len(text))]
    results = engine.analyze(passages)

    hits = results[0]
    pattern_ids = {h.pattern_id for h in hits}
    assert "OP-01" in pattern_ids
    assert "BZ-01" in pattern_ids
