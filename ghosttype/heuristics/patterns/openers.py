"""Generic opening phrase patterns."""

PATTERNS = [
    {
        "id": "OP-01",
        "category": "opener",
        "regex": r"in today'?s (?:fast-paced )?(?:world|society|era|environment)",
        "severity": 0.8,
        "description": "Temporal universalism opener",
    },
    {
        "id": "OP-02",
        "category": "opener",
        "regex": r"it is (?:important|crucial|essential|vital) to (?:note|understand|recognize) that",
        "severity": 0.8,
        "description": "Importance declaration opener",
    },
    {
        "id": "OP-03",
        "category": "opener",
        "regex": r"when it comes to|in the realm of|in the field of|in the world of",
        "severity": 0.8,
        "description": "Topic announcement opener",
    },
    {
        "id": "OP-04",
        "category": "opener",
        "regex": r"have you ever wondered|what if i told you|imagine a world where",
        "severity": 0.8,
        "description": "Rhetorical question opener",
    },
    {
        "id": "OP-05",
        "category": "opener",
        "regex": r"\w+ is defined as|according to (?:merriam-webster|the dictionary|wikipedia)",
        "severity": 0.8,
        "description": "Definition stall opener",
    },
    {
        "id": "OP-06",
        "category": "opener",
        "regex": r"in an era of|in a world where|in the age of",
        "severity": 0.8,
        "description": "Era framing opener",
    },
    {
        "id": "OP-07",
        "category": "opener",
        "regex": r"let us begin by|to start with|before we begin",
        "severity": 0.7,
        "description": "Meta-discursive opener",
    },
    {
        "id": "OP-08",
        "category": "opener",
        "regex": r"the question of whether|the issue of|the problem of",
        "severity": 0.7,
        "description": "Topic formulation opener",
    },
    {
        "id": "OP-09",
        "category": "opener",
        "regex": r"as we all know|as is well known|it is widely accepted",
        "severity": 0.7,
        "description": "Universal knowledge claim opener",
    },
    {
        "id": "OP-10",
        "category": "opener",
        "regex": r"with the advent of|since the emergence of|following the rise of",
        "severity": 0.7,
        "description": "Historical framing opener",
    },
]
