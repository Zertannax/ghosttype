"""French buzzword cluster patterns."""

PATTERNS = [
    {
        "id": "FBZ-01",
        "category": "french_buzzword",
        "regex": r"(?i)\bsynergie\b|\blevier\b|\btransformation digitale\b|\bmétamorphose\b",
        "severity": 0.6,
        "description": "Buzzword management FR",
    },
    {
        "id": "FBZ-02",
        "category": "french_buzzword",
        "regex": r"(?i)\bapproche holistique\b|\bvision globale\b|\bperspective d'ensemble\b",
        "severity": 0.6,
        "description": "Buzzword holistique FR",
    },
    {
        "id": "FBZ-03",
        "category": "french_buzzword",
        "regex": r"(?i)\bdynamique\b|\becosystème\b|\bparadigme\b|\bcadre stratégique\b",
        "severity": 0.6,
        "description": "Buzzword systémique FR",
    },
    {
        "id": "FBZ-04",
        "category": "french_buzzword",
        "regex": r"(?i)\boptimisation\b|\befficience\b|\bperformance opérationnelle\b|\bexcellence opérationnelle\b",
        "severity": 0.6,
        "description": "Buzzword optimisation FR",
    },
    {
        "id": "FBZ-05",
        "category": "french_buzzword",
        "regex": r"(?i)\bdisruption\b|\brupture technologique\b|\binnovation disruptive\b|\btransformation profonde\b",
        "severity": 0.9,
        "description": "Buzzword disruption FR (haute confiance)",
    },
    {
        "id": "FBZ-06",
        "category": "french_buzzword",
        "regex": r"(?i)\bcatalyseur\b|\baccelerateur\b|\bfactor d'acceleration\b",
        "severity": 0.6,
        "description": "Buzzword catalyseur FR",
    },
    {
        "id": "FBZ-07",
        "category": "french_buzzword",
        "regex": r"(?i)\bdurabilité\b|\bscalabilité\b|\bresilience\b|\badaptabilité\b",
        "severity": 0.6,
        "description": "Buzzword qualités systémiques FR",
    },
    {
        "id": "FBZ-08",
        "category": "french_buzzword",
        "regex": r"(?i)\balignement stratégique\b|\bconvergence des\b|\barticulation entre\b",
        "severity": 0.6,
        "description": "Buzzword alignment FR",
    },
]
