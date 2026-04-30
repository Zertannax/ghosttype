"""Semantic scoring using fastembed embeddings."""


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


def _get_embedding_model() -> "TextEmbedding":
    """Get or create the embedding model."""
    if not FASTEMBED_AVAILABLE:
        raise ImportError("fastembed is not installed. Install with: poetry add fastembed")
    return TextEmbedding(model_name=DEFAULT_MODEL)


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
    """Compute semantic slop scores for passages.

    Uses a simple heuristic: measures text formality/structure patterns
    that correlate with AI-generated text.

    Args:
        passages: List of passages.

    Returns:
        List of scores 0.0-1.0 per passage.
    """
    if not FASTEMBED_AVAILABLE or not passages:
        return [0.5] * len(passages)

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
            "dans une perspective", "dynamique", "synergie",
            "holistique", "strategique", "optimisation",
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
            # Low variance = more AI-like
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
