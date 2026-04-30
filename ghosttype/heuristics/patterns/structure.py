"""Over-structure patterns."""

PATTERNS = [
    {
        "id": "ST-01",
        "category": "structure",
        "regex": r"firstly[,.]?\s+.*?secondly[,.]?\s+.*?thirdly[,.]?|first[,.]?\s+.*?second[,.]?\s+.*?third[,.]?",
        "severity": 0.7,
        "description": "Ordinal sequencing",
    },
    {
        "id": "ST-02",
        "category": "structure",
        "regex": r"there are \d+ key (?:aspects|points|factors|elements|considerations)",
        "severity": 0.7,
        "description": "Aspect listing",
    },
    {
        "id": "ST-03",
        "category": "structure",
        "regex": r"in this (?:section|chapter|part|article),? (?:we will|I will|let us|let's)",
        "severity": 0.7,
        "description": "Paragraph signposting",
    },
    {
        "id": "ST-04",
        "category": "structure",
        "regex": r"^(?:in conclusion|to summarize|in summary|to conclude)[,.]",
        "severity": 0.7,
        "description": "Conclusion marker at paragraph start",
    },
    {
        "id": "ST-05",
        "category": "structure",
        "regex": r"having established (?:that|this|the)|we can now turn to|let us now consider",
        "severity": 0.7,
        "description": "Transition narration",
    },
    {
        "id": "ST-06",
        "category": "structure",
        "regex": r"it is important to note that|worth noting|important to mention",
        "severity": 0.6,
        "description": "Meta-commentary on structure",
    },
]
