"""Journalist-style AI patterns and human-oratory negative indicators (English-only).

Pattern IDs are kept stable across the FR purge (2026-05). Removed FR-specific
entries (JR-01, 03, 05, 07, 09, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22) along
with the French listicle and oratory variants. EN classical-oratory detectors
(JR-21/23/24) were rewritten in English so the human-indicator bonus actually
fires on Churchill/MLK-style prose.
"""

PATTERNS = [
    {
        "id": "JR-02",
        "category": "journalist_setup",
        "regex": r"\bhere'?s why\b|\blet me explain\b|\bhere'?s the thing\b|\bthe short answer is\b",
        "severity": 0.6,
        "description": "EN journalistic setup phrase",
    },
    {
        "id": "JR-04",
        "category": "journalist_revelation",
        "regex": r"\bexcept that\b|\bthe real signal\b|\bwhat few people\b|\bwhat nobody tells you\b|\bthe key element\b",
        "severity": 0.7,
        "description": "EN journalistic revelation",
    },
    {
        "id": "JR-06",
        "category": "journalist_rhetorical",
        "regex": r"\bwhy now\b|\bwhat does it change\b|\bwhat if\b,|\bimagine a world\b|\bhave you noticed\b",
        "severity": 0.5,
        "description": "EN rhetorical question opener",
    },
    {
        "id": "JR-08",
        "category": "journalist_conclusion",
        "regex": r"\bwhat it means\b|\bthe takeaway\b|\bbottom line\b|\blong story short\b|\bin short,",
        "severity": 0.6,
        "description": "EN journalistic conclusion",
    },
    {
        "id": "JR-10",
        "category": "journalist_implicit",
        "regex": r"\bit'?s written in black and white\b|\bit goes without saying\b|\bnobody can deny\b",
        "severity": 0.6,
        "description": "EN implicit assertion",
    },
    {
        "id": "JR-20",
        "category": "journalist_stats_dump",
        "regex": r"\d+[.,]?\d*\s*%\s*(?:on|of|in|against|vs\.?)|\d+\s*out\s*of\s*\d+|\d+-fold|\d+x\s*faster",
        "severity": 0.5,
        "description": "EN statistics dump pattern",
    },
    {
        "id": "JR-21",
        "category": "classical_oratory",
        "regex": r"\bmy fellow (?:countrymen|citizens|americans)\b|\bfellow citizens\b|\bdear friends\b|\bmy friends,",
        "severity": -0.4,
        "description": "Classical EN oratory address (Churchill/MLK/Lincoln/Kennedy style)",
    },
    {
        "id": "JR-23",
        "category": "classical_oratory",
        "regex": r"\bI (?:do not|don'?t) say [^.]{1,40}\bI say\b|\bnot [^,]{1,30}, but [^,]{1,30}\b|\bI have nothing to offer\b|\bI tell you\b",
        "severity": -0.3,
        "description": "Self-correcting / declarative rhetorical construction (human speech)",
    },
    {
        "id": "JR-24",
        "category": "classical_oratory",
        "regex": r"\bwe shall (?:fight|defend|never|go on)\b|\blet us (?:not |be |go )\b|\bI have a dream\b|\bblood, (?:toil|sweat|tears)\b|\bask not what\b",
        "severity": -0.5,
        "description": "Anaphora and famous oratorical formulas (human, high-confidence negative)",
    },
    {
        "id": "JR-25",
        "category": "ai_listicle",
        "regex": r"\btop\s+\d+\b|\b\d+\s+ways\s+to\b|\b\d+\s+reasons\b|\b\d+\s+things\s+(?:you|we|to know)\b",
        "severity": 0.7,
        "description": "Listicle format (strong AI / clickbait indicator)",
    },
    {
        "id": "JR-26",
        "category": "ai_modern_formatting",
        "regex": r"👉|💡|⚠️|🔥|🚀|✅|❌|📊|📈|⬇️|⬆️",
        "severity": 0.8,
        "description": "Emoji formatting (modern AI social media style)",
    },
    {
        "id": "JR-27",
        "category": "ai_bullet_points",
        "regex": r"^\s*[•\-*]\s|\n\s*[•\-*]\s",
        "severity": 0.5,
        "description": "Bullet point formatting (common in AI summaries)",
    },
]
