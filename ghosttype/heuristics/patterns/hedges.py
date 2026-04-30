"""Hedge filler patterns."""

PATTERNS = [
    {
        "id": "HE-01",
        "category": "hedge",
        "regex": r"it is (?:worth|important|crucial) (?:noting|mentioning|to note)",
        "severity": 0.5,
        "description": "Epistemic hedge",
    },
    {
        "id": "HE-02",
        "category": "hedge",
        "regex": r"one could argue|some might say|many would agree|it could be argued",
        "severity": 0.5,
        "description": "Soft assertion hedge",
    },
    {
        "id": "HE-03",
        "category": "hedge",
        "regex": r"at the end of the day|when all is said and done|(?:ultimately|finally),?\s*(?:it is clear|we can see)",
        "severity": 0.5,
        "description": "Temporal hedge",
    },
    {
        "id": "HE-04",
        "category": "hedge",
        "regex": r"to some extent|in many ways|in a sense|to a certain degree",
        "severity": 0.5,
        "description": "Scope limiter hedge",
    },
    {
        "id": "HE-05",
        "category": "hedge",
        "regex": r"^(?:certainly|absolutely|of course),?\s+(?:it is|we can|this is)",
        "severity": 0.5,
        "description": "Affirmation starter hedge",
    },
]
