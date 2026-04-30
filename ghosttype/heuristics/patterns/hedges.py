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
    {
        "id": "HE-06",
        "category": "hedge",
        "regex": r"arguably|presumably|reportedly|allegedly",
        "severity": 0.5,
        "description": "Evidential hedge",
    },
    {
        "id": "HE-07",
        "category": "hedge",
        "regex": r"in (?:general|most cases|many instances)|broadly speaking",
        "severity": 0.5,
        "description": "Generalization hedge",
    },
    {
        "id": "HE-08",
        "category": "hedge",
        "regex": r"more or less|to a large extent|by and large",
        "severity": 0.5,
        "description": "Approximation hedge",
    },
    {
        "id": "HE-09",
        "category": "hedge",
        "regex": r"it seems (?:that|to be|as if)|it appears that",
        "severity": 0.5,
        "description": "Perceptual hedge",
    },
    {
        "id": "HE-10",
        "category": "hedge",
        "regex": r"it goes without saying|needless to say|it is understood",
        "severity": 0.5,
        "description": "Assumed agreement hedge",
    },
]
