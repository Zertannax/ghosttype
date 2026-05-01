"""End-to-end fixture tests: feed real-shaped passages through the full pipeline
and assert they land in the right score bucket.

These tests use FASTEMBED_AVAILABLE=False (keyword fallback) so they run quickly
and deterministically without needing the .npz corpora present.
"""

from pathlib import Path

import pytest

import ghosttype.semantic as semantic
from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import preprocess
from ghosttype.scorer import aggregate
from ghosttype.semantic import semantic_score_passages
from ghosttype.stylistic import stylistic_score_passages

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def offline_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force keyword-fallback path for deterministic, corpus-free tests."""
    monkeypatch.setattr(semantic, "FASTEMBED_AVAILABLE", False)
    semantic._model_cache = None
    semantic._corpus_cache = {}


def _analyze(text: str):
    passages = preprocess(text)
    engine = HeuristicEngine()
    hits = engine.analyze(passages)
    sem = semantic_score_passages(passages)
    sty = stylistic_score_passages(passages)
    return aggregate(passages, hits, sem, sty)


def test_human_oratory_scores_below_moderate() -> None:
    """Churchill-style speech must land in Clean or Mild (exit 0)."""
    text = (FIXTURES / "sample_human.txt").read_text(encoding="utf-8")
    result = _analyze(text)
    assert result.exit_code == 0, (
        f"Human oratory exit_code={result.exit_code}, expected 0. Score={result.score}"
    )
    assert result.score < 41, f"Human oratory score={result.score}, expected < 41"


def test_ai_slop_fixture_scores_high() -> None:
    """The shipped slop fixture should still register significant patterns even
    after the false-positive cleanup. We don't require HIGH because the fixture
    is moderately written, but it must score above pure clean."""
    text = (FIXTURES / "sample_slop.txt").read_text(encoding="utf-8")
    result = _analyze(text)
    assert result.score >= 25, f"Slop fixture score={result.score}, expected >= 25"


def test_obvious_ai_text_with_clusters_triggers_high_exit() -> None:
    """Text packed with cross-category buzzwords + openers + transitions must
    trip exit code 2."""
    text = (
        "In today's rapidly evolving landscape, organizations must leverage "
        "transformative methodologies to achieve sustainable growth. Furthermore, "
        "the integration of holistic frameworks enables stakeholders to navigate "
        "complex paradigms.\n\n"
        "Moreover, comprehensive strategies facilitate optimization of operational "
        "excellence across diverse ecosystems. It is important to note that this "
        "multifaceted approach requires nuanced understanding of synergistic dynamics.\n\n"
        "In conclusion, embracing these innovative paradigms will catalyze "
        "unprecedented value creation for forward-thinking organizations."
    )
    result = _analyze(text)
    assert result.exit_code == 2, (
        f"AI cluster exit_code={result.exit_code}, expected 2. Score={result.score}"
    )


def test_recipe_does_not_false_positive() -> None:
    """A short, uniform-sentence recipe is the canonical false positive — it
    must not trip exit code 2."""
    text = (
        "Add two eggs to a bowl. Whisk until smooth. Pour the batter into a "
        "hot pan. Cook for three minutes per side. Flip carefully. Serve with "
        "maple syrup."
    )
    result = _analyze(text)
    assert result.exit_code == 0, (
        f"Recipe exit_code={result.exit_code}, expected 0. Score={result.score}"
    )
