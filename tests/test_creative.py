"""Tests for creative writing pattern detection (fiction / storytelling AI)."""

import pytest

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.heuristics.patterns.creative import PATTERNS as CREATIVE
from ghosttype.preprocessor import Passage


@pytest.fixture
def engine() -> HeuristicEngine:
    return HeuristicEngine()


def _passage(text: str) -> Passage:
    return Passage(index=0, text=text, start_char=0, end_char=len(text))


# ---------- module shape ----------

def test_creative_module_has_15_patterns() -> None:
    """ROADMAP v0.5.0 calls for 15 creative writing patterns."""
    assert len(CREATIVE) == 15


def test_creative_pattern_ids_unique_and_well_formed() -> None:
    ids = [p["id"] for p in CREATIVE]
    assert len(set(ids)) == 15
    for id_ in ids:
        assert id_.startswith("CR-")


def test_creative_severities_in_range() -> None:
    for p in CREATIVE:
        assert -1.0 <= p["severity"] <= 1.0


# ---------- specific tells fire ----------

@pytest.mark.parametrize("text,pattern_id", [
    ("It was a dark and stormy night when she arrived.", "CR-01"),
    ("Once upon a time, in a faraway kingdom, there lived a queen.", "CR-01"),
    ("She gazed at him with cerulean eyes that held the weight of centuries.", "CR-02"),
    ("His emerald gaze pierced through the morning fog.", "CR-02"),
    ("She felt a wave of sadness wash over her as the door closed.", "CR-03"),
    ("A surge of relief flooded through him.", "CR-03"),
    ("His heart skipped a beat when he heard the familiar voice.", "CR-04"),
    ("Her eyes hitched on the photograph in the corner.", "CR-04"),
    ("An eerie silence settled over the empty courtyard.", "CR-06"),
    ("The air hung thick with unspoken words.", "CR-06"),
    ("She whispered softly into the darkness.", "CR-07"),
    ("Their eyes met across the crowded room.", "CR-08"),
    ("The garden was bathed in golden light at dusk.", "CR-09"),
    ("In that moment, she knew everything would change.", "CR-10"),
    ("She couldn't help but smile at his earnestness.", "CR-11"),
    ("Her thoughts swirled like leaves in a storm.", "CR-12"),
    ("A shiver ran down her spine as the temperature dropped.", "CR-15"),
    ("His blood ran cold at the mere mention of the name.", "CR-15"),
])
def test_creative_pattern_fires_on_canonical_tell(
    engine: HeuristicEngine, text: str, pattern_id: str
) -> None:
    """Each creative pattern catches its canonical AI fiction phrase."""
    hits = engine.analyze([_passage(text)])[0]
    found_ids = {h.pattern_id for h in hits}
    assert pattern_id in found_ids, (
        f"Expected {pattern_id} to fire on '{text}'. Got: {sorted(found_ids)}"
    )


# ---------- false-positive guard on real human prose ----------

@pytest.mark.parametrize("text", [
    # Orwell, 1984 — terse, observed prose
    "He took out a small pocketbook and wrote a few words in it.",
    # Hemingway-like, plain
    "The old man caught the fish at dawn. The water was cold.",
    # Plain factual sentence
    "The cat sat on the mat. It was warm and sunny.",
    # Standard descriptive sentence — should NOT trigger
    "She looked out the window and saw the garden.",
])
def test_creative_patterns_quiet_on_plain_prose(
    engine: HeuristicEngine, text: str
) -> None:
    """No creative pattern should fire on plain unadorned prose."""
    hits = engine.analyze([_passage(text)])[0]
    creative_hits = [h for h in hits if h.pattern_id.startswith("CR-")]
    assert not creative_hits, (
        f"Plain prose triggered creative patterns: "
        f"{[(h.pattern_id, h.matched_text) for h in creative_hits]}"
    )


# ---------- aggregate effect on a typical AI fiction passage ----------

def test_ai_fiction_sample_clusters_creative_patterns(engine: HeuristicEngine) -> None:
    """An AI-style fiction paragraph should hit multiple CR-* patterns at once."""
    sample = (
        "Their eyes met across the moonlit garden, bathed in silver light. "
        "She felt a wave of longing, and her heart skipped a beat. In that "
        "moment, she knew her life would never be the same. A shiver ran "
        "down her spine."
    )
    hits = engine.analyze([_passage(sample)])[0]
    creative_ids = {h.pattern_id for h in hits if h.pattern_id.startswith("CR-")}
    assert len(creative_ids) >= 4, (
        f"Expected 4+ distinct creative patterns, got {sorted(creative_ids)}"
    )
