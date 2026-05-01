"""Tests for stylistic feature extraction and scoring."""

from ghosttype.preprocessor import Passage
from ghosttype.stylistic import (
    StylisticFeatures,
    extract_features,
    stylistic_score_passages,
)


def _passage(text: str, idx: int = 0) -> Passage:
    return Passage(index=idx, text=text, start_char=0, end_char=len(text))


# ---------- extract_features shape ----------

def test_extract_features_returns_all_fields() -> None:
    """All eight feature fields are populated for any non-empty input."""
    f = extract_features(_passage("This is a sentence. Here is another one."))
    assert isinstance(f, StylisticFeatures)
    for field in (
        "sentence_variance", "paragraph_variance", "avg_word_length",
        "punctuation_density", "rare_word_ratio", "formal_word_ratio",
        "neutrality_score", "ai_score",
    ):
        v = getattr(f, field)
        assert isinstance(v, float), f"{field} not a float"
        assert 0.0 <= v <= 1.0, f"{field}={v} outside [0, 1]"


def test_extract_features_empty_text_safe() -> None:
    """Empty passage doesn't crash — returns neutral defaults."""
    f = extract_features(_passage(""))
    assert 0.0 <= f.ai_score <= 1.0


# ---------- recipe / short-form must NOT score high ----------

def test_recipe_short_uniform_sentences_skip_variance_test() -> None:
    """The variance trick (uniform short sentences) must not flag a recipe as AI."""
    recipe = "Add eggs. Mix well. Pour batter. Bake 30 min. Cool 10 min. Serve."
    f = extract_features(_passage(recipe))
    # Floor at 0.5 means the variance signal was correctly skipped.
    assert f.sentence_variance == 0.5
    assert f.ai_score < 0.5, f"Recipe scored {f.ai_score}, expected < 0.5"


def test_short_paragraphs_skip_paragraph_variance_test() -> None:
    """Bullet-list-like input doesn't fall into the paragraph-variance trap."""
    bullets = "First point.\n\nSecond point.\n\nThird point.\n\nFourth point."
    f = extract_features(_passage(bullets))
    assert f.paragraph_variance == 0.5


# ---------- AI buzzword density ----------

def test_emotional_human_text_scores_lower_than_uniform_neutral_text() -> None:
    """The stylistic scorer measures uniformity + neutrality, so emotional human
    writing should score lower than emotionally-flat text of similar length.

    This guards the neutrality_score path more than the buzzword path —
    buzzword detection is the heuristic engine's job, not stylistic.
    """
    emotional_human = (
        "I cannot believe how amazing this is! I am thrilled, ecstatic, "
        "delighted beyond measure. The gorgeous sunset broke my heart. "
        "What a magnificent, wonderful day this has been."
    )
    flat_neutral = (
        "The report indicates that the system performs adequately. "
        "Operations continue as scheduled. The quarterly review meeting "
        "will be held on Thursday. Subsequent updates will follow."
    )
    emo_score = extract_features(_passage(emotional_human)).ai_score
    flat_score = extract_features(_passage(flat_neutral)).ai_score
    assert emo_score < flat_score, (
        f"Emotional human={emo_score} should score lower than flat neutral={flat_score}"
    )


def test_formal_word_ratio_picks_up_academic_transitions() -> None:
    """Stacked academic transitions raise formal_word_ratio above 0."""
    text = (
        "Furthermore, the analysis suggests it. Moreover, consequently, the data confirms it. "
        "Therefore, however, the conclusion stands. Nevertheless, alternatively, we could ask."
    )
    f = extract_features(_passage(text))
    assert f.formal_word_ratio > 0.0


# ---------- neutrality ----------

def test_neutrality_high_for_neutral_text() -> None:
    text = "The conference takes place on Tuesday. The agenda will be circulated next week."
    f = extract_features(_passage(text))
    assert f.neutrality_score > 0.9


def test_neutrality_drops_with_emotional_words() -> None:
    text = "I love this beautiful book. It is wonderful, brilliant, amazing. I am thrilled and delighted."
    f = extract_features(_passage(text))
    assert f.neutrality_score < 1.0


# ---------- document-level wrapper ----------

def test_score_passages_empty_returns_neutral() -> None:
    assert stylistic_score_passages([]) == 0.5


def test_score_passages_in_range_for_mixed_input() -> None:
    passages = [
        _passage("In today's evolving landscape we leverage synergy."),
        _passage("The cat sat quietly."),
    ]
    score = stylistic_score_passages(passages)
    assert 0.0 <= score <= 1.0
