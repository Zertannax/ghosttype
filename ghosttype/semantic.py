"""Semantic scoring using fastembed embeddings and cosine similarity."""

from pathlib import Path

import numpy as np

from ghosttype.preprocessor import Passage

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False

# Default model for embeddings
DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"

# Weights for semantic scoring
SEMANTIC_WEIGHT = 0.45
HEURISTIC_WEIGHT = 0.55

# Corpus paths
DATA_DIR = Path(__file__).parent / "data"
HUMAN_CORPUS = DATA_DIR / "human_corpus.npz"
SLOP_CORPUS = DATA_DIR / "slop_corpus.npz"


def _get_embedding_model() -> "TextEmbedding":
    """Get or create the embedding model."""
    if not FASTEMBED_AVAILABLE:
        raise ImportError("fastembed is not installed. Install with: poetry add fastembed")
    return TextEmbedding(model_name=DEFAULT_MODEL)


def _load_corpus(corpus_path: Path) -> np.ndarray | None:
    """Load embeddings from .npz file."""
    if not corpus_path.exists():
        return None
    data = np.load(corpus_path)
    embeddings: np.ndarray = data["embeddings"]
    return embeddings


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between vectors.

    Args:
        a: Array shape (n, d)
        b: Array shape (m, d)

    Returns:
        Similarity matrix shape (n, m)
    """
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    result: np.ndarray = np.dot(a_norm, b_norm.T)
    return result


def embed_passages(passages: list[Passage]) -> np.ndarray:
    """Embed passages using fastembed.

    Args:
        passages: List of passages to embed.

    Returns:
        Array of embeddings shape (n_passages, embedding_dim).
    """
    if not passages:
        return np.array([])

    model = _get_embedding_model()
    texts = [p.text for p in passages]
    embeddings = list(model.embed(texts))
    return np.array(embeddings)


def compute_semantic_scores(passages: list[Passage]) -> list[float]:
    """Compute semantic slop scores for passages using embeddings.

    Compares passage embeddings against human and slop reference corpora.
    Returns score based on similarity ratio.

    Args:
        passages: List of passages.

    Returns:
        List of scores 0.0-1.0 per passage.
    """
    if not FASTEMBED_AVAILABLE or not passages:
        return [0.5] * len(passages)

    # Load reference corpora
    human_embeddings = _load_corpus(HUMAN_CORPUS)
    slop_embeddings = _load_corpus(SLOP_CORPUS)

    if human_embeddings is None or slop_embeddings is None:
        # Fallback to keyword-based scoring if corpora not available
        return _keyword_based_scores(passages)

    # Embed input passages
    passage_embeddings = embed_passages(passages)

    scores = []
    for emb in passage_embeddings:
        # Compute similarities to both corpora
        sim_human = _cosine_similarity(emb.reshape(1, -1), human_embeddings).mean()
        sim_slop = _cosine_similarity(emb.reshape(1, -1), slop_embeddings).mean()

        # Score: high sim_slop / (sim_slop + sim_human) = more slop-like
        score = sim_slop / (sim_slop + sim_human) if sim_slop + sim_human > 0 else 0.5

        scores.append(min(1.0, max(0.0, score)))

    return scores


def _keyword_based_scores(passages: list[Passage]) -> list[float]:
    """Fallback keyword-based scoring when embeddings unavailable."""
    scores = []
    for passage in passages:
        text = passage.text.lower()
        score = 0.0

        # Formal/structured language indicators
        formal_markers = [
            "furthermore", "moreover", "consequently", "therefore",
            "nevertheless", "nonetheless", "alternatively",
            "in conclusion", "to summarize", "in summary",
            "it is important", "it should be noted", "it is worth",
            "on one hand", "on the other hand",
            "not only", "but also",
            "dans une perspective", "il convient", "force est",
            "par ailleurs", "en somme", "en definitive",
        ]

        for marker in formal_markers:
            if marker in text:
                score += 0.05

        # Corporate/AI buzzword density
        buzzwords = [
            "leverage", "synergy", "holistic", "robust", "strategic",
            "comprehensive", "innovative", "disruptive", "scalable",
            "sustainable", "optimize", "streamline", "facilitate",
            "paradigm", "framework", "ecosystem", "landscape",
            "synergie", "dynamique", "holistique", "strategique",
            "optimisation", "disruption", "catalyseur",
        ]

        for buzz in buzzwords:
            if buzz in text:
                score += 0.08

        # Sentence length variance (AI tends uniform lengths)
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        if len(sentences) > 2:
            lengths = [len(s) for s in sentences]
            avg_len = sum(lengths) / len(lengths)
            variance = sum((length - avg_len) ** 2 for length in lengths) / len(lengths)
            if variance < 100:
                score += 0.1

        scores.append(min(1.0, score))

    return scores


def semantic_score_passages(passages: list[Passage]) -> float:
    """Compute overall semantic score for a document.

    Args:
        passages: List of passages.

    Returns:
        Semantic score 0.0-1.0.
    """
    if not passages:
        return 0.5

    passage_scores = compute_semantic_scores(passages)
    # Weight by passage length
    weights = [len(p.text) for p in passages]
    total_weight = sum(weights)

    if total_weight == 0:
        return 0.5

    weighted_score = sum(s * w for s, w in zip(passage_scores, weights, strict=False)) / total_weight
    return min(1.0, max(0.0, weighted_score))
