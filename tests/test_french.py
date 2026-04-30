"""Tests for French pattern detection."""

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import Passage


def test_french_opener() -> None:
    """Test detection of French opener."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="Dans un monde en constante évolution, nous devons agir.", start_char=0, end_char=55)]
    results = engine.analyze(passages)

    assert any(h.pattern_id == "FOP-01" for h in results[0])


def test_french_hedge() -> None:
    """Test detection of French hedge."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="Il convient de noter que cela fonctionne.", start_char=0, end_char=41)]
    results = engine.analyze(passages)

    assert any(h.pattern_id == "FHE-01" for h in results[0])


def test_french_buzzword() -> None:
    """Test detection of French buzzword."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="C'est une approche holistique.", start_char=0, end_char=31)]
    results = engine.analyze(passages)

    assert any(h.pattern_id == "FBZ-02" for h in results[0])


def test_french_high_severity() -> None:
    """Test high severity French disruption buzzword."""
    engine = HeuristicEngine()
    passages = [Passage(index=0, text="C'est une innovation disruptive.", start_char=0, end_char=32)]
    results = engine.analyze(passages)

    hits = results[0]
    fbz05_hits = [h for h in hits if h.pattern_id == "FBZ-05"]
    assert len(fbz05_hits) > 0
    assert fbz05_hits[0].severity == 0.9
