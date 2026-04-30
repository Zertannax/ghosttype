# GhostType

> Detect AI-generated slop in any text. Score it. Rewrite it.

```
$ ghosttype analyze essay.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GhostType — AI Slop Detector v0.1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Slop Score : 73/100  ██████████░░░░  HIGH
  Patterns   : 8 detected
  Passages   : 3 flagged for rewrite

  [!] "In today's fast-paced world..."     → generic opener
  [!] "It is worth noting that..."         → hedge filler
  [!] "This comprehensive approach..."     → buzzword cluster

  Run with --rewrite to get suggestions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## What is AI slop?

AI slop = text that is technically correct but stylistically hollow. Generic openers, filler hedges, buzzword clusters, over-structured paragraphs, fake balance. You know it when you read it. GhostType scores it.

## Install

```bash
# Clone the repository
git clone https://github.com/Zertannax/ghosttype.git
cd ghosttype

# Install dependencies with Poetry
poetry install

# Or install in development mode
pip install -e ".[dev]"
```

## Usage

```bash
# Basic analysis (reads file or stdin)
ghosttype analyze text.txt

# Analyze stdin
echo "In today's fast-paced world..." | ghosttype analyze -

# JSON output for piping
ghosttype analyze text.txt --json | jq '.passages'

# Show version
ghosttype version
```

## Scoring

Score is 0–100. Higher = more sloppy.

| Range | Label | What it means |
|-------|-------|---------------|
| 0–20 | Clean | Human voice, specific, grounded |
| 21–40 | Mild | Some generic phrasing, mostly ok |
| 41–60 | Moderate | Noticeable patterns, worth reviewing |
| 61–80 | High | Heavy slop, rewrites recommended |
| 81–100 | Critical | Almost certainly AI-generated as-is |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Score < 40 (clean) |
| 1 | Score 40–70 (moderate) |
| 2 | Score > 70 (high slop) |

Exit codes enable shell scripting: `ghosttype analyze draft.txt || echo "too sloppy"`

## Stack

- **Core detection:** heuristics + rule engine (see `PATTERNS.md`)
- **Semantic scoring:** fastembed / sentence-transformers (planned for v0.2)
- **Rewrite engine:** Ollama local LLM (planned for v0.2)
- **CLI:** typer + rich
- **API (optional):** FastAPI (planned for v0.2)

## Development

```bash
# Setup
poetry install

# Run tests
poetry run pytest

# Lint and format
poetry run ruff check .
poetry run ruff format .

# Type check
poetry run mypy ghosttype/
```

## Project structure

```
ghosttype/
├── ghosttype/              # Package principal
│   ├── cli.py              # CLI entry point
│   ├── preprocessor.py     # Text segmentation
│   ├── scorer.py           # Score aggregation
│   ├── semantic.py         # Semantic scorer (planned)
│   ├── rewriter.py         # LLM rewrite engine (planned)
│   ├── heuristics/
│   │   ├── engine.py       # Pattern orchestration
│   │   └── patterns/       # Pattern definitions
│   │       ├── openers.py
│   │       ├── hedges.py
│   │       ├── buzzwords.py
│   │       ├── structure.py (planned)
│   │       ├── balance.py (planned)
│   │       └── transitions.py (planned)
│   └── data/               # Reference corpora (planned)
├── tests/                  # Test suite
├── scripts/                # GHCLI helpers
├── README.md
├── ARCHITECTURE.md
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
├── AGENTS.md
├── GHCLI.md
└── pyproject.toml
```

## License

MIT
