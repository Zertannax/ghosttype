"""Text preprocessing and segmentation."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Passage:
    """A segmented text passage."""

    index: int
    text: str
    start_char: int
    end_char: int


def _strip_html(text: str) -> str:
    """Remove basic HTML tags."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&amp;", "&", text)
    return text


def _segment_paragraphs(text: str) -> list[Passage]:
    """Split text on double newlines."""
    passages: list[Passage] = []
    position = 0
    index = 0

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split on double newlines
    raw_paragraphs = re.split(r"\n\s*\n", text)

    for raw in raw_paragraphs:
        start = text.find(raw, position)
        if start == -1:
            start = position
        end = start + len(raw)
        cleaned = raw.strip()
        if cleaned:
            passages.append(Passage(index=index, text=cleaned, start_char=start, end_char=end))
            index += 1
        position = end

    return passages


def _segment_sentences(text: str) -> list[Passage]:
    """Fallback: split on sentence boundaries."""
    passages: list[Passage] = []
    # Simple regex for sentence splitting
    sentence_pattern = r"[^.!?]+[.!?]+\s*"
    matches = list(re.finditer(sentence_pattern, text))

    if not matches:
        # If no sentences found, treat entire text as one passage
        cleaned = text.strip()
        if cleaned:
            return [Passage(index=0, text=cleaned, start_char=0, end_char=len(text))]
        return []

    for idx, match in enumerate(matches):
        sentence = match.group().strip()
        if sentence:
            passages.append(
                Passage(
                    index=idx,
                    text=sentence,
                    start_char=match.start(),
                    end_char=match.end(),
                )
            )

    return passages


def preprocess(text: str) -> list[Passage]:
    """Preprocess and segment text into passages.

    Args:
        text: Raw input text.

    Returns:
        List of Passage objects.
    """
    text = _strip_html(text)
    passages = _segment_paragraphs(text)

    if not passages:
        passages = _segment_sentences(text)

    return passages


def preprocess_file(path: Path) -> list[Passage]:
    """Read and preprocess a file.

    Args:
        path: Path to text file.

    Returns:
        List of Passage objects.
    """
    text = path.read_text(encoding="utf-8")
    return preprocess(text)
