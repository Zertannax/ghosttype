"""AI transition phrase patterns."""

PATTERNS = [
    {
        "id": "TR-01",
        "category": "transition",
        "regex": r"furthermore[,;]?\s+|moreover[,;]?\s+|additionally[,;]?\s+",
        "severity": 0.5,
        "description": "Additive transitions (clustered)",
    },
    {
        "id": "TR-02",
        "category": "transition",
        "regex": r"however[,;]?\s+it is important to|nevertheless[,;]?\s+one must consider",
        "severity": 0.5,
        "description": "Contrastive fillers",
    },
    {
        "id": "TR-03",
        "category": "transition",
        "regex": r"to elaborate on this point|to put it another way|in other words[,;]?\s+this means",
        "severity": 0.5,
        "description": "Elaboration signals",
    },
    {
        "id": "TR-04",
        "category": "transition",
        "regex": r"as a result of this[,;]?|consequently[,;]?\s+|therefore[,;]?\s+",
        "severity": 0.5,
        "description": "Consequence chains (overused)",
    },
    {
        "id": "TR-05",
        "category": "transition",
        "regex": r"in addition to this|on top of that|what is more",
        "severity": 0.5,
        "description": "Extra additive transitions",
    },
    {
        "id": "TR-06",
        "category": "transition",
        "regex": r"(?:it is|this is) (?:clear|evident|apparent|obvious) that",
        "severity": 0.5,
        "description": "Ostensible obviousness",
    },
]
