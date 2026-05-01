"""Tests for text preprocessor."""

from ghosttype.preprocessor import _segment_sentences, preprocess


def test_preprocess_simple_paragraphs() -> None:
    """Test basic paragraph segmentation."""
    text = "First paragraph.\n\nSecond paragraph."
    passages = preprocess(text)

    assert len(passages) == 2
    assert passages[0].text == "First paragraph."
    assert passages[0].index == 0
    assert passages[1].text == "Second paragraph."
    assert passages[1].index == 1


def test_preprocess_single_paragraph() -> None:
    """Test single paragraph input."""
    text = "Only one paragraph here."
    passages = preprocess(text)

    assert len(passages) == 1
    assert passages[0].text == "Only one paragraph here."


def test_preprocess_strips_html() -> None:
    """Test HTML stripping."""
    text = "<p>Hello world</p>"
    passages = preprocess(text)

    assert len(passages) == 1
    assert "<p>" not in passages[0].text
    assert passages[0].text == "Hello world"


def test_preprocess_empty_text() -> None:
    """Test empty text handling."""
    passages = preprocess("")
    assert passages == []


def test_preprocess_whitespace_only() -> None:
    """Test whitespace-only text."""
    passages = preprocess("   \n\n   ")
    assert passages == []


def test_preprocess_single_block_stays_one_passage() -> None:
    """Text without blank lines is a single paragraph (paragraph segmenter wins)."""
    text = "First sentence. Second sentence! Third sentence?"
    passages = preprocess(text)
    assert len(passages) == 1
    assert passages[0].text == text


def test_segment_sentences_splits_on_punctuation() -> None:
    """Direct test of the sentence segmenter (unreachable via preprocess in practice)."""
    text = "First sentence. Second sentence! Third sentence?"
    passages = _segment_sentences(text)
    assert len(passages) == 3
    assert passages[0].text.startswith("First")
    assert passages[1].text.startswith("Second")
    assert passages[2].text.startswith("Third")


def test_preprocess_strips_html_entities() -> None:
    """Named HTML entities &amp; &lt; &gt; are decoded."""
    text = "<p>Tom &amp; Jerry &lt;3 each other &gt; all</p>"
    passages = preprocess(text)
    assert len(passages) == 1
    assert "&amp;" not in passages[0].text
    assert "&" in passages[0].text  # decoded
    assert "<" in passages[0].text  # decoded from &lt;
    assert ">" in passages[0].text  # decoded from &gt;
