"""Tests for text preprocessor."""

from ghosttype.preprocessor import preprocess


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


def test_preprocess_fallback_sentences() -> None:
    """Test sentence fallback for no paragraphs."""
    text = "First sentence. Second sentence! Third sentence?"
    passages = preprocess(text)

    # Should still work with paragraph split (single paragraph)
    assert len(passages) >= 1
    assert "First sentence." in passages[0].text
