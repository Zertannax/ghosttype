"""Stylistic feature detection for AI-generated text."""

import re
from dataclasses import dataclass

from ghosttype.preprocessor import Passage


@dataclass
class StylisticFeatures:
    """Collection of stylistic features for a passage."""

    sentence_variance: float
    paragraph_variance: float
    avg_word_length: float
    punctuation_density: float
    rare_word_ratio: float
    formal_word_ratio: float
    neutrality_score: float
    ai_score: float


def extract_features(passage: Passage) -> StylisticFeatures:
    """Extract stylistic features from a passage.

    Args:
        passage: Text passage.

    Returns:
        StylisticFeatures with computed metrics.
    """
    text = passage.text
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b\w+\b', text)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Sentence length variance (AI tends uniform lengths)
    # Skip the test for recipe/list/instruction-style text where short uniform
    # sentences are the natural form, not an AI tell.
    if len(sentences) >= 3:
        lengths = [len(s) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        if avg_len < 30:
            # Short-form text (recipes, instructions): variance signal is meaningless.
            sentence_variance = 0.5
        else:
            variance = sum((length - avg_len) ** 2 for length in lengths) / len(lengths)
            sentence_variance = min(1.0, max(0.0, 1.0 - (variance / 500)))
    else:
        sentence_variance = 0.5

    # Paragraph length variance (AI tends very uniform paragraph lengths)
    if len(paragraphs) >= 3:
        para_word_counts = [len(p.split()) for p in paragraphs]
        avg_para = sum(para_word_counts) / len(para_word_counts)
        if avg_para < 20:
            # Short paragraphs (lists, bullets): variance signal is meaningless.
            paragraph_variance = 0.5
        else:
            para_variance = sum((c - avg_para) ** 2 for c in para_word_counts) / len(para_word_counts)
            paragraph_variance = min(1.0, max(0.0, 1.0 - (para_variance / 300)))
    else:
        paragraph_variance = 0.5

    # Average word length (AI tends longer/formal words)
    if words:
        avg_word_length = sum(len(w) for w in words) / len(words)
        # Normalize: 4-5 chars = neutral, >6 = AI-like
        avg_word_length = min(1.0, max(0.0, (avg_word_length - 4.0) / 3.0))
    else:
        avg_word_length = 0.5

    # Punctuation density (AI tends regular punctuation)
    punct_count = len(re.findall(r'[,.;:!?]', text))
    if len(text) > 0:
        punct_density = punct_count / len(text)
        # Normalize: 0.05-0.10 = normal, >0.12 = AI-like
        punctuation_density = min(1.0, max(0.0, (punct_density - 0.05) / 0.10))
    else:
        punctuation_density = 0.0

    # Rare word ratio (AI tends common/predictable words)
    common_words = {
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
        "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    }
    if words:
        rare_count = sum(1 for w in words if w.lower() not in common_words)
        rare_word_ratio = 1.0 - (rare_count / len(words))
    else:
        rare_word_ratio = 0.5

    # Formal word ratio (AI tends formal vocabulary)
    # Note: "however"/"therefore" included here because frequency (rather than
    # presence) is the signal. Bare prepositions like "par"/"dans" were removed —
    # they are too common to be AI markers on their own.
    formal_words = {
        "furthermore", "moreover", "consequently", "therefore", "however",
        "nevertheless", "nonetheless", "alternatively", "specifically",
        "particularly", "essentially", "fundamentally", "significantly",
        "notably", "accordingly", "subsequently", "hence", "thus",
    }
    if words:
        formal_count = sum(1 for w in words if w.lower() in formal_words)
        formal_word_ratio = min(1.0, formal_count / len(words) * 5)
    else:
        formal_word_ratio = 0.0

    # Neutrality score (AI text is very emotionally neutral)
    emotional_words = {
        "love", "hate", "amazing", "terrible", "awful", "wonderful", "brilliant",
        "stupid", "ridiculous", "fantastic", "horrible", "beautiful", "ugly",
        "excited", "bored", "angry", "happy", "sad", "frustrated", "thrilled",
        "devastated", "ecstatic", "furious", "delighted", "miserable",
        "gorgeous", "dreadful", "magnificent", "appalling", "splendid",
        "joyful", "heartbroken", "outraged", "elated", "disgusted",
    }
    if words:
        emotional_count = sum(1 for w in words if w.lower() in emotional_words)
        # High neutrality = low emotional word ratio
        neutrality_score = 1.0 - min(1.0, emotional_count / len(words) * 10)
    else:
        neutrality_score = 0.5

    # Combined AI score
    ai_score = (
        sentence_variance * 0.2 +
        paragraph_variance * 0.25 +
        avg_word_length * 0.1 +
        punctuation_density * 0.1 +
        rare_word_ratio * 0.15 +
        formal_word_ratio * 0.1 +
        neutrality_score * 0.1
    )

    return StylisticFeatures(
        sentence_variance=sentence_variance,
        paragraph_variance=paragraph_variance,
        avg_word_length=avg_word_length,
        punctuation_density=punctuation_density,
        rare_word_ratio=rare_word_ratio,
        formal_word_ratio=formal_word_ratio,
        neutrality_score=neutrality_score,
        ai_score=ai_score,
    )


def stylistic_score_passages(passages: list[Passage]) -> float:
    """Compute overall stylistic score for a document.

    Args:
        passages: List of passages.

    Returns:
        Stylistic score 0.0-1.0.
    """
    if not passages:
        return 0.5

    scores = []
    weights = []
    for passage in passages:
        features = extract_features(passage)
        scores.append(features.ai_score)
        weights.append(len(passage.text))

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.5

    weighted_score = sum(s * w for s, w in zip(scores, weights, strict=False)) / total_weight
    return min(1.0, max(0.0, weighted_score))
