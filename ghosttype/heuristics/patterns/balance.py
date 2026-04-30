"""Fake balance patterns."""

PATTERNS = [
    {
        "id": "FB-01",
        "category": "balance",
        "regex": r"on one hand.*?on the other hand",
        "severity": 0.6,
        "description": "Classic both-sides",
    },
    {
        "id": "FB-02",
        "category": "balance",
        "regex": r"while .+? has advantages?[,;]? it also has disadvantages?",
        "severity": 0.6,
        "description": "Advantages/disadvantages frame",
    },
    {
        "id": "FB-03",
        "category": "balance",
        "regex": r"proponents argue.*?critics contend|supporters claim.*?opponents argue",
        "severity": 0.6,
        "description": "Proponents/critics frame without resolution",
    },
    {
        "id": "FB-04",
        "category": "balance",
        "regex": r"the issue is complex and multifaceted|a complex and nuanced issue|this is a multifaceted problem",
        "severity": 0.6,
        "description": "Complexity acknowledgment without unpacking",
    },
]
