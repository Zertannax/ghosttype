"""Tests for semantic scoring — focus on graceful degradation paths."""

from pathlib import Path

import numpy as np
import pytest

import ghosttype.semantic as semantic
from ghosttype.preprocessor import Passage
from ghosttype.semantic import (
    EMBEDDING_DIM,
    _cosine_similarity,
    _keyword_based_scores,
    _load_corpus,
    compute_semantic_scores,
    semantic_score_passages,
)


@pytest.fixture(autouse=True)
def reset_caches() -> None:
    """Each test gets a clean module-level cache."""
    semantic._model_cache = None
    semantic._corpus_cache = {}


def _passage(text: str, idx: int = 0) -> Passage:
    return Passage(index=idx, text=text, start_char=0, end_char=len(text))


# ---------- offline / fallback paths ----------

def test_compute_scores_empty_input_returns_empty() -> None:
    assert compute_semantic_scores([]) == []


def test_compute_scores_falls_back_when_fastembed_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without fastembed installed, must still return scores via keyword fallback."""
    monkeypatch.setattr(semantic, "FASTEMBED_AVAILABLE", False)
    passages = [_passage("In today's rapidly evolving landscape, we must leverage synergy.")]
    scores = compute_semantic_scores(passages)
    assert len(scores) == 1
    assert 0.0 <= scores[0] <= 1.0
    # Buzzword-heavy text should score above baseline
    assert scores[0] > 0.0


def test_compute_scores_falls_back_when_corpus_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Even with fastembed available, missing corpora must trigger keyword fallback
    rather than crashing or returning 0.5 sentinels."""
    monkeypatch.setattr(semantic, "HUMAN_CORPUS", tmp_path / "missing_human.npz")
    monkeypatch.setattr(semantic, "SLOP_CORPUS", tmp_path / "missing_slop.npz")
    passages = [_passage("Furthermore, we leverage our holistic framework.")]
    scores = compute_semantic_scores(passages)
    assert len(scores) == 1
    assert scores[0] > 0.0  # keyword fallback activated, not the sentinel 0.5


def test_keyword_fallback_scores_clean_text_low() -> None:
    """Plain neutral prose hits no keyword markers."""
    passages = [_passage("The cat sat on the mat. It was warm and sunny outside.")]
    scores = _keyword_based_scores(passages)
    assert scores[0] == 0.0


def test_keyword_fallback_scores_buzzword_heavy_high() -> None:
    """Buzzword-heavy prose accumulates score from keyword + buzzword markers."""
    text = (
        "In today's evolving landscape, we leverage synergy and strategic frameworks. "
        "Furthermore, our holistic, scalable, sustainable approach is comprehensive."
    )
    passages = [_passage(text)]
    scores = _keyword_based_scores(passages)
    assert scores[0] > 0.3


# ---------- _load_corpus validation ----------

def test_load_corpus_missing_returns_none_and_caches(tmp_path: Path) -> None:
    p = tmp_path / "nope.npz"
    assert _load_corpus(p) is None
    assert p in semantic._corpus_cache  # negative result cached
    assert _load_corpus(p) is None  # second call hits cache


def test_load_corpus_wrong_dim_returns_none(tmp_path: Path) -> None:
    p = tmp_path / "bad_dim.npz"
    np.savez(p, embeddings=np.zeros((10, 99)))  # 99 != 384
    assert _load_corpus(p) is None


def test_load_corpus_wrong_shape_returns_none(tmp_path: Path) -> None:
    p = tmp_path / "bad_shape.npz"
    np.savez(p, embeddings=np.zeros(384))  # 1D not 2D
    assert _load_corpus(p) is None


def test_load_corpus_missing_key_returns_none(tmp_path: Path) -> None:
    p = tmp_path / "wrong_key.npz"
    np.savez(p, vectors=np.zeros((10, EMBEDDING_DIM)))  # key 'vectors', not 'embeddings'
    assert _load_corpus(p) is None


def test_load_corpus_valid_returns_array_and_caches(tmp_path: Path) -> None:
    p = tmp_path / "good.npz"
    np.savez(p, embeddings=np.random.rand(50, EMBEDDING_DIM))
    arr1 = _load_corpus(p)
    arr2 = _load_corpus(p)
    assert arr1 is not None
    assert arr1.shape == (50, EMBEDDING_DIM)
    # Cache returns the same array object
    assert arr2 is arr1


# ---------- _cosine_similarity NaN guard ----------

def test_cosine_zero_norm_gives_zero_not_nan() -> None:
    zero = np.zeros((1, EMBEDDING_DIM))
    other = np.random.rand(3, EMBEDDING_DIM)
    sim = _cosine_similarity(zero, other)
    assert sim.shape == (1, 3)
    assert not np.isnan(sim).any()
    assert (sim == 0.0).all()


def test_cosine_both_zero_gives_zero() -> None:
    z1 = np.zeros((2, EMBEDDING_DIM))
    z2 = np.zeros((4, EMBEDDING_DIM))
    sim = _cosine_similarity(z1, z2)
    assert sim.shape == (2, 4)
    assert not np.isnan(sim).any()
    assert (sim == 0.0).all()


def test_cosine_orthogonal_unit_vectors_close_to_zero() -> None:
    a = np.zeros((1, EMBEDDING_DIM))
    a[0, 0] = 1.0
    b = np.zeros((1, EMBEDDING_DIM))
    b[0, 1] = 1.0
    sim = _cosine_similarity(a, b)
    assert abs(sim[0, 0]) < 1e-9


def test_cosine_identical_unit_vectors_one() -> None:
    a = np.zeros((1, EMBEDDING_DIM))
    a[0, 0] = 1.0
    sim = _cosine_similarity(a, a)
    assert abs(sim[0, 0] - 1.0) < 1e-9


# ---------- semantic_score_passages document-level ----------

def test_document_score_empty_returns_neutral() -> None:
    assert semantic_score_passages([]) == 0.5


def test_document_score_in_range(monkeypatch: pytest.MonkeyPatch) -> None:
    """Document score must always land in [0, 1] regardless of fastembed availability."""
    monkeypatch.setattr(semantic, "FASTEMBED_AVAILABLE", False)
    passages = [
        _passage("In today's evolving landscape we leverage synergy."),
        _passage("The cat sat quietly."),
    ]
    score = semantic_score_passages(passages)
    assert 0.0 <= score <= 1.0
