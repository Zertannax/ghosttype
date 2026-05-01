# GhostType

> Detect AI-generated slop in any text. Score it.

```
$ ghosttype analyze essay.txt
==================================================
  GhostType - AI Slop Detector v0.4.2
==================================================

  Slop Score : 73/100  ██████████░░░░  HIGH
  Patterns   : 8 detected
  Passages   : 3 analyzed

  Flagged Passages
  #  Text                                    Score  Hits
  1  In today's fast-paced world, the...       73     8

  Pattern Details
  Pattern  Category     Matched Text                 Severity
  OP-01    opener       In today's fast-paced world...  0.8
  HE-01    hedge        It is worth noting that...      0.5
  BZ-03    buzzword     groundbreaking approach...      0.6
  ...

==================================================
```

## What is AI slop?

AI slop = text that is technically correct but stylistically hollow. Generic openers, filler hedges, buzzword clusters, over-structured paragraphs, fake balance, neutral framing. You know it when you read it. GhostType scores it 0-100.

## Features

- **75+ heuristic patterns** across 8 categories: generic openers, hedge fillers, buzzword clusters, over-structure, fake balance, AI transitions, journalist conventions, conversational slop, academic markers, technical markers
- **Semantic scoring**: fastembed embedding similarity vs 975 AI + 1000 human reference passages (BAAI/bge-small-en-v1.5, 384-dim)
- **Stylistic analysis**: sentence length variance, paragraph uniformity, word rarity, punctuation density, neutrality detection
- **Human indicator bonus**: detects classical oratory (Churchill, MLK, Socrates) and genuine human emotion to reduce false positives on real human text
- **Rich CLI output** with ASCII-safe characters (Windows-compatible)
- **JSON output** for piping and automation
- **Exit codes** for shell scripting integration

## Install

```bash
# Clone the repository
git clone https://github.com/Zertannax/ghosttype.git
cd ghosttype

# Install with Poetry
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
ghosttype analyze text.txt --json | jq '.score'

# Show version
ghosttype version
```

## Scoring

Score is 0-100. Higher = more sloppy.

| Range | Label | What it means |
|-------|-------|---------------|
| 0-20 | Clean | Human voice, specific, grounded |
| 21-40 | Mild | Some generic phrasing, mostly ok |
| 41-60 | Moderate | Noticeable patterns, worth reviewing |
| 61-80 | High | Heavy slop, rewrites recommended |
| 81-100 | Critical | Almost certainly AI-generated as-is |

### Score composition

Final score = weighted combination of three signals:
- **Heuristic** (40%): pattern matches across all categories
- **Semantic** (30%): embedding similarity to AI vs human corpus
- **Stylistic** (30%): statistical text features
- **Human bonus** (-5 to -50): classical oratory/emotion detection reduces score

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Score <= 40 (Clean / Mild) |
| 1 | Score 41-60 (Moderate) |
| 2 | Score >= 61 (High / Critical) |

Exit codes enable shell scripting:
```bash
ghosttype analyze draft.txt || echo "too sloppy"
```

## Detection Categories

| Category | Count | Description |
|----------|-------|-------------|
| Generic Openers | 5 | Temporal universalism, importance declarations |
| Hedge Fillers | 5 | Epistemic hedges, soft assertions |
| Buzzword Clusters | 5 | Synergy vocab, impact theater, AI self-description |
| Over-Structure | 5 | Firstly/Secondly/Finally, paragraph signposting |
| Fake Balance | 4 | Both-sides framing, pro/con without resolution |
| AI Transitions | 4 | Furthermore, Moreover, Consequently (clustered) |
| Journalist Patterns | 27 | Conventional phrases, unsupported claims, accumulation, classical oratory (negative severity) |
| Conversational Slop | 15 | ChatGPT neutral framing, fake humility, hedging |
| Academic Markers | 15 | Research paper conventions, passive voice, literature review |
| Technical Markers | 15 | Documentation steps, commands, configuration |
| **Total** | **~110** | English-only |

## Reference Corpora

| Corpus | Passages | Source |
|--------|----------|--------|
| AI slop | 975 | RAID (llama-chat, mpt) + Falcon RefinedWeb |
| Human | 1000 | RAID human + Falcon human |
| Model | BAAI/bge-small-en-v1.5 | 384-dim, ~130MB |

Embeddings are pre-built and shipped as `.npz` files — no GPU required at runtime.

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

## Project Structure

```
ghosttype/
├── ghosttype/
│   ├── cli.py              # CLI entry point (typer + rich)
│   ├── preprocessor.py     # Text segmentation
│   ├── scorer.py           # Score aggregation (heuristic + semantic + stylistic)
│   ├── semantic.py         # fastembed embedding scorer
│   ├── stylistic.py        # Statistical text analysis
│   ├── heuristics/
│   │   ├── engine.py       # Pattern orchestration
│   │   └── patterns/       # Pattern definitions
│   │       ├── openers.py
│   │       ├── hedges.py
│   │       ├── buzzwords.py
│   │       ├── structure.py
│   │       ├── balance.py
│   │       ├── transitions.py
│   │       ├── journalist.py
│   │       ├── conversational.py
│   │       ├── academic.py
│   │       └── technical.py
│   └── data/
│       ├── slop_corpus.npz     # AI reference embeddings (975, 384)
│       ├── human_corpus.npz    # Human reference embeddings (1000, 384)
│       └── corpus_meta.json    # Corpus metadata
├── tests/                  # Test suite
├── scripts/                # Dataset download + corpus build
│   ├── download_datasets.py
│   ├── download_falcon.py
│   └── build_corpus.py
├── README.md
├── ARCHITECTURE.md
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
├── CHANGELOG.md
├── AGENTS.md
├── GHCLI.md
└── pyproject.toml
```

## License

MIT
