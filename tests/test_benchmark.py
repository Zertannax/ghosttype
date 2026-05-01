"""Tests for the benchmark script's loader and metrics — pure unit tests,
no real corpus access."""

import sys
from pathlib import Path

import pytest

# Make scripts/ importable as a module path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import benchmark  # noqa: E402


# ---------- _load_jsonl_texts ----------

def test_load_jsonl_skips_short_and_malformed(tmp_path: Path) -> None:
    p = tmp_path / "mix.jsonl"
    long_text = " ".join(["word"] * 40)  # >= 30 words → kept
    short_text = "too short"             # < 30 words → skipped
    p.write_text(
        '{"text": "' + long_text + '"}\n'
        '{"text": "' + short_text + '"}\n'
        'not json at all\n'
        '{"no_text_field": true}\n'
        '\n',
        encoding="utf-8",
    )
    samples = benchmark._load_jsonl_texts(p)
    assert len(samples) == 1
    assert samples[0][0] == long_text
    assert samples[0][1] == "mix.jsonl"


def test_load_jsonl_missing_file_returns_empty(tmp_path: Path) -> None:
    assert benchmark._load_jsonl_texts(tmp_path / "absent.jsonl") == []


# ---------- compute_metrics ----------

def _sample(label: str, score: int) -> benchmark.Sample:
    return benchmark.Sample(label=label, source="test", text="x", score=score)


def test_metrics_perfect_classifier() -> None:
    samples = [_sample("ai", 90), _sample("ai", 80), _sample("human", 10), _sample("human", 20)]
    m = benchmark.compute_metrics(samples, threshold=50)
    assert m.tp == 2 and m.tn == 2 and m.fp == 0 and m.fn == 0
    assert m.precision == 1.0
    assert m.recall == 1.0
    assert m.f1 == 1.0
    assert m.accuracy == 1.0


def test_metrics_all_wrong() -> None:
    samples = [_sample("ai", 10), _sample("ai", 20), _sample("human", 90), _sample("human", 80)]
    m = benchmark.compute_metrics(samples, threshold=50)
    assert m.tp == 0 and m.tn == 0
    assert m.fp == 2 and m.fn == 2
    assert m.f1 == 0.0
    assert m.accuracy == 0.0


def test_metrics_threshold_is_strict_greater_than() -> None:
    """A score equal to the threshold should NOT count as AI prediction."""
    samples = [_sample("ai", 50), _sample("human", 50)]
    m = benchmark.compute_metrics(samples, threshold=50)
    # Both predicted human → AI sample is FN, human sample is TN
    assert m.tp == 0
    assert m.fn == 1
    assert m.tn == 1
    assert m.fp == 0


def test_metrics_zero_division_safe_on_empty() -> None:
    m = benchmark.compute_metrics([], threshold=50)
    assert m.precision == 0.0
    assert m.recall == 0.0
    assert m.f1 == 0.0
    assert m.accuracy == 0.0


# ---------- score_text smoke ----------

def test_score_text_runs_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """End-to-end smoke: score_text returns an int in [0, 100] for any non-empty text."""
    import ghosttype.semantic as sem
    monkeypatch.setattr(sem, "FASTEMBED_AVAILABLE", False)
    sem._model_cache = None
    sem._corpus_cache = {}

    from ghosttype.heuristics.engine import HeuristicEngine
    score = benchmark.score_text(HeuristicEngine(), "The cat sat on the mat. It was warm and sunny outside today.")
    assert isinstance(score, int)
    assert 0 <= score <= 100
