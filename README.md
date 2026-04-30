# GhostType

> Detect AI-generated slop in any text. Score it. Rewrite it.

```
$ ghosttype analyze essay.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GHOSTTYPE — AI Slop Detector v0.1.0
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

## Two modes

| Mode | Requirements | What it does |
|------|-------------|--------------|
| `--no-llm` | Nothing | Heuristics + embeddings. Fast, offline, runs anywhere. |
| `--llm` | Ollama + 4B model | Adds rewrite suggestions via local LLM. |

Both modes give a slop score. The LLM only adds rewrites.

## Install

```bash
# With pip
pip install ghosttype

# From source
git clone https://github.com/yourname/ghosttype
cd ghosttype
pip install -e ".[dev]"
```

## Usage

```bash
# Basic analysis
ghosttype analyze text.txt

# Analyze stdin
echo "In today's fast-paced world..." | ghosttype analyze -

# With rewrite suggestions (requires Ollama)
ghosttype analyze essay.txt --rewrite --model qwen2.5:3b

# JSON output for piping
ghosttype analyze text.txt --json | jq '.passages'

# Web UI (optional, requires: pip install ghosttype[web])
ghosttype serve --port 8080
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

## Stack

- **Core detection:** heuristics + rule engine (see `PATTERNS.md`)
- **Semantic scoring:** `fastembed` / `sentence-transformers`
- **Rewrite engine:** Ollama local LLM (Qwen2.5-3B or Phi-3.5-mini)
- **CLI:** `typer` + `rich`
- **API (optional):** `FastAPI`
- **Web UI (optional):** lightweight, no framework

## License

MIT
