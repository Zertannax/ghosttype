"""French generic opening phrase patterns."""

PATTERNS = [
    {
        "id": "FOP-01",
        "category": "french_opener",
        "regex": r"dans un monde (?:en constante évolution|qui change rapidement|de plus en plus complexe)",
        "severity": 0.8,
        "description": "Ouverture temporelle universelle FR",
    },
    {
        "id": "FOP-02",
        "category": "french_opener",
        "regex": r"il est (?:important|essentiel|crucial|indispensable) de (?:noter|comprendre|souligner) que",
        "severity": 0.8,
        "description": "Déclaration d'importance FR",
    },
    {
        "id": "FOP-03",
        "category": "french_opener",
        "regex": r"en ce qui concerne|s'agissant de|lorsqu'il est question de",
        "severity": 0.8,
        "description": "Annonce de sujet FR",
    },
    {
        "id": "FOP-04",
        "category": "french_opener",
        "regex": r"à l'ère de|dans l'ère du|depuis l'avènement de",
        "severity": 0.8,
        "description": "Cadrage historique FR",
    },
    {
        "id": "FOP-05",
        "category": "french_opener",
        "regex": r"force est de constater|il convient de reconnaître|nul ne peut nier",
        "severity": 0.8,
        "description": "Assertion universelle FR",
    },
]
