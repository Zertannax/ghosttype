"""Buzzword cluster patterns."""

PATTERNS = [
    {
        "id": "BZ-01",
        "category": "buzzword",
        "regex": r"(?i)\bsynergy\b|\bleverage\b|\bparadigm shift\b|\bgame-changer\b",
        "severity": 0.6,
        "description": "Synergy vocabulary",
    },
    {
        "id": "BZ-02",
        "category": "buzzword",
        "regex": r"(?i)\bcomprehensive\b|\bholistic\b|\brobust\b|\bcutting-edge\b",
        "severity": 0.6,
        "description": "Comprehensiveness buzzword",
    },
    {
        "id": "BZ-03",
        "category": "buzzword",
        "regex": r"(?i)\btransformative\b|\bgroundbreaking\b|\brevolutionary\b|\binnovative\b",
        "severity": 0.6,
        "description": "Impact theater buzzword",
    },
    {
        "id": "BZ-04",
        "category": "buzzword",
        "regex": r"(?i)\bfacilitate\b|\butilize\b|\bimplement solutions\b|\bstrategic\b",
        "severity": 0.6,
        "description": "Process language buzzword",
    },
    {
        "id": "BZ-05",
        "category": "buzzword",
        "regex": r"(?i)\bdelve\b|\btapestry\b|\bnuanced understanding\b|\bmultifaceted\b",
        "severity": 0.9,
        "description": "AI self-description buzzword (high confidence)",
    },
]
