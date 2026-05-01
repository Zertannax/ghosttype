"""Semantic scoring using fastembed embeddings and cosine similarity.

Resilient to three failure modes:
- fastembed not installed → keyword fallback
- reference corpora .npz missing or malformed → keyword fallback
- zero-norm embeddings (empty / pathological input) → 0.0 similarity, never NaN

The embedding model and the loaded corpora are cached at module level so a single
process re-embeds nothing across calls.
"""

import logging
import math
from pathlib import Path
from typing import Optional

import numpy as np

from ghosttype.preprocessor import Passage

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False
    TextEmbedding = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

# Top-k nearest neighbors used per corpus when scoring a passage. A flat .mean()
# over 975+ corpus passages washed out the signal — averaging only the K closest
# slop / human passages preserves locality while staying robust to single noisy
# neighbors.
TOP_K = 10

DATA_DIR = Path(__file__).parent / "data"
HUMAN_CORPUS = DATA_DIR / "human_corpus.npz"
SLOP_CORPUS = DATA_DIR / "slop_corpus.npz"

# Module-level caches — model load + corpus load are both expensive.
_model_cache: Optional["TextEmbedding"] = None
_corpus_cache: dict[Path, Optional[np.ndarray]] = {}


def _get_embedding_model() -> "TextEmbedding":
    """Return the singleton embedding model, creating it on first call."""
    global _model_cache
    if not FASTEMBED_AVAILABLE:
        raise ImportError("fastembed is not installed. Install with: poetry add fastembed")
    if _model_cache is None:
        _model_cache = TextEmbedding(model_name=DEFAULT_MODEL)
    return _model_cache


def _load_corpus(corpus_path: Path) -> Optional[np.ndarray]:
    """Load reference embeddings from .npz, validating shape. Cached per path.

    Returns None (and logs a warning) if the file is missing, malformed, or has
    a dimension other than EMBEDDING_DIM. Callers must treat None as a signal
    to fall back to keyword scoring.
    """
    if corpus_path in _corpus_cache:
        return _corpus_cache[corpus_path]

    if not corpus_path.exists():
        logger.warning(
            "Reference corpus not found: %s. Falling back to keyword scoring.",
            corpus_path,
        )
        _corpus_cache[corpus_path] = None
        return None

    try:
        with np.load(corpus_path) as data:
            if "embeddings" not in data.files:
                raise KeyError("missing 'embeddings' key")
            embeddings = data["embeddings"].copy()
    except (OSError, KeyError, ValueError) as e:
        logger.warning("Failed to load corpus %s: %s. Falling back to keyword scoring.", corpus_path, e)
        _corpus_cache[corpus_path] = None
        return None

    if embeddings.ndim != 2 or embeddings.shape[1] != EMBEDDING_DIM:
        logger.warning(
            "Corpus %s has unexpected shape %s, expected (n, %d). Ignoring.",
            corpus_path, embeddings.shape, EMBEDDING_DIM,
        )
        _corpus_cache[corpus_path] = None
        return None

    _corpus_cache[corpus_path] = embeddings
    return embeddings


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity matrix between two batches, safe against zero norms.

    Args:
        a: shape (n, d)
        b: shape (m, d)

    Returns:
        Similarity matrix shape (n, m), values in [-1, 1]. Zero-norm rows produce
        0.0 instead of NaN.
    """
    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)
    a_safe = np.divide(a, a_norm, out=np.zeros_like(a, dtype=float), where=a_norm > 0)
    b_safe = np.divide(b, b_norm, out=np.zeros_like(b, dtype=float), where=b_norm > 0)
    result = np.dot(a_safe, b_safe.T)
    return np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)


def embed_passages(passages: list[Passage]) -> np.ndarray:
    """Embed passages using fastembed in a single batched call."""
    if not passages:
        return np.zeros((0, EMBEDDING_DIM), dtype=float)
    model = _get_embedding_model()
    texts = [p.text for p in passages]
    embeddings = list(model.embed(texts))
    return np.array(embeddings, dtype=float)


def compute_semantic_scores(passages: list[Passage]) -> list[float]:
    """Compute semantic slop scores for each passage.

    Routes to the keyword fallback when fastembed is unavailable OR when the
    reference corpora cannot be loaded. The corpus-based path returns a
    sim_slop / (sim_slop + sim_human) ratio, clamped to [0, 1] and NaN-guarded.

    Args:
        passages: List of passages.

    Returns:
        List of scores 0.0-1.0, one per passage (empty list if input is empty).
    """
    if not passages:
        return []

    if not FASTEMBED_AVAILABLE:
        return _keyword_based_scores(passages)

    human_embeddings = _load_corpus(HUMAN_CORPUS)
    slop_embeddings = _load_corpus(SLOP_CORPUS)

    if human_embeddings is None or slop_embeddings is None:
        return _keyword_based_scores(passages)

    passage_embeddings = embed_passages(passages)

    scores: list[float] = []
    for emb in passage_embeddings:
        sim_human = _topk_mean(_cosine_similarity(emb.reshape(1, -1), human_embeddings)[0])
        sim_slop = _topk_mean(_cosine_similarity(emb.reshape(1, -1), slop_embeddings)[0])

        denom = sim_slop + sim_human
        if denom > 0 and not math.isnan(denom):
            score = sim_slop / denom
        else:
            score = 0.5

        if math.isnan(score):
            score = 0.5
        scores.append(min(1.0, max(0.0, score)))

    return scores


def _topk_mean(similarities: np.ndarray, k: int = TOP_K) -> float:
    """Mean of the top-k highest similarities. Falls back to plain mean if k > len."""
    if similarities.size == 0:
        return 0.0
    k_eff = min(k, similarities.size)
    # np.partition gives the k largest in the last k positions (unordered, fine for mean).
    top_k = np.partition(similarities, -k_eff)[-k_eff:]
    return float(top_k.mean())


def _keyword_based_scores(passages: list[Passage]) -> list[float]:
    """Fallback keyword-based scoring when embeddings are unavailable.

    Cheap heuristic: count formal markers and corporate buzzwords, plus a
    sentence-length-uniformity kicker. Calibrated to land roughly in
    [0.0, 0.7] so that downstream weights still mix it with heuristics.
    """
    formal_markers = (
        "furthermore", "moreover", "consequently", "therefore",
        "nevertheless", "nonetheless", "alternatively",
        "in conclusion", "to summarize", "in summary",
        "it is important", "it should be noted", "it is worth",
        "on one hand", "on the other hand",
        "not only", "but also",
    )
    buzzwords = (
        "leverage", "synergy", "holistic", "robust", "strategic",
        "comprehensive", "innovative", "disruptive", "scalable",
        "sustainable", "optimize", "streamline", "facilitate",
        "paradigm", "framework", "ecosystem", "landscape",
    )

    scores: list[float] = []
    for passage in passages:
        text = passage.text.lower()
        score = 0.0

        score += 0.05 * sum(1 for m in formal_markers if m in text)
        score += 0.08 * sum(1 for b in buzzwords if b in text)

        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if len(sentences) > 2:
            lengths = [len(s) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            if avg_len >= 30:  # skip short-form text (recipes, lists)
                variance = sum((length - avg_len) ** 2 for length in lengths) / len(lengths)
                if variance < 100:
                    score += 0.1

        scores.append(min(1.0, max(0.0, score)))

    return scores


def semantic_score_passages(passages: list[Passage]) -> float:
    """Compute the document-level semantic score (length-weighted mean of passages)."""
    if not passages:
        return 0.5

    passage_scores = compute_semantic_scores(passages)
    if not passage_scores:
        return 0.5

    weights = [len(p.text) for p in passages]
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.5

    weighted_score = sum(s * w for s, w in zip(passage_scores, weights, strict=True)) / total_weight
    if math.isnan(weighted_score):
        return 0.5
    return min(1.0, max(0.0, weighted_score))
