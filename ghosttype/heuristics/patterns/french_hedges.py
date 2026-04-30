"""French hedge filler patterns."""

PATTERNS = [
    {
        "id": "FHE-01",
        "category": "french_hedge",
        "regex": r"il convient de (?:noter|mentionner|souligner) que",
        "severity": 0.5,
        "description": "Hedge épistémique FR",
    },
    {
        "id": "FHE-02",
        "category": "french_hedge",
        "regex": r"on pourrait dire|certains diront|il est admis que",
        "severity": 0.5,
        "description": "Assertion adoucie FR",
    },
    {
        "id": "FHE-03",
        "category": "french_hedge",
        "regex": r"en définitive|en fin de compte|à terme|à la longue",
        "severity": 0.5,
        "description": "Hedge temporel FR",
    },
    {
        "id": "FHE-04",
        "category": "french_hedge",
        "regex": r"dans une certaine mesure|dans une large mesure|jusqu'à un certain point",
        "severity": 0.5,
        "description": "Restriction de portée FR",
    },
    {
        "id": "FHE-05",
        "category": "french_hedge",
        "regex": r"sans doute|vraisemblablement|probablement|de toute évidence",
        "severity": 0.5,
        "description": "Hedge de probabilité FR",
    },
]
