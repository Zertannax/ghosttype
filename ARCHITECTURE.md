# GhostType — Architecture

## Overview

GhostType is a pipeline: text in → scored passages out → optional rewrites.

```
Input (file / stdin / API)
        │
        ▼
┌───────────────────┐
│   Preprocessor    │  Tokenize, segment into passages, clean whitespace
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Heuristic Engine │  Rule-based pattern matching (fast, deterministic)
│   (always on)     │  Output: pattern hits per passage
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Semantic Scorer  │  Embedding similarity vs slop/human reference corpora
│   (always on)     │  Output: semantic slop score 0.0–1.0
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Score Aggregator│  Weighted combination → final score 0–100
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 Report    [Optional]
 (CLI/JSON) Rewrite Engine (LLM via Ollama)
```

---

## Modules

### 1. Preprocessor (`ghosttype/preprocessor.py`)

**Responsibility:** normalize and segment input text.

```python
@dataclass
class Passage:
    index: int
    text: str
    start_char: int
    end_char: int
```

- Split on paragraphs (double newline) by default
- Fallback: sentence segmentation via simple regex (no NLTK dependency for --no-llm mode)
- Strip HTML if detected

---

### 2. Heuristic Engine (`ghosttype/heuristics/`)

**Responsibility:** pattern-based detection. Fast, deterministic, explainable.

Structure:
```
ghosttype/heuristics/
  __init__.py
  engine.py         # orchestrates all detectors
  patterns/
    openers.py      # generic opening phrases
    hedges.py       # filler hedges and qualifiers
    buzzwords.py    # corporate/AI buzzword clusters
    structure.py    # over-structured patterns (firstly/secondly/finally)
    balance.py      # fake balance ("on one hand... on the other hand...")
    transitions.py  # AI transition phrases
```

Each detector returns:
```python
@dataclass
class PatternHit:
    pattern_id: str
    category: str          # "opener" | "hedge" | "buzzword" | etc.
    matched_text: str
    start_char: int
    end_char: int
    severity: float        # 0.0–1.0
```

Weight table (tunable via config):
| Category | Default weight |
|----------|---------------|
| opener | 0.8 |
| hedge | 0.5 |
| buzzword | 0.6 |
| structure | 0.7 |
| balance | 0.6 |
| transition | 0.5 |

---

### 3. Semantic Scorer (`ghosttype/semantic.py`)

**Responsibility:** embedding-based similarity to reference corpora.

Two reference corpora (embedded at build time, shipped as small `.npz` files):
- `slop_corpus`: ~500 passages from HC3 + RAID benchmark (AI-generated)
- `human_corpus`: ~500 passages from Project Gutenberg + Reddit writing subs (human)

At runtime:
1. Embed input passage via `fastembed` (model: `BAAI/bge-small-en-v1.5`, ~130MB)
2. Compute cosine similarity to slop centroid and human centroid
3. Score = normalized distance ratio

```python
semantic_score = sim_to_slop / (sim_to_slop + sim_to_human)
# 0.0 = very human-like, 1.0 = very slop-like
```

**Offline fallback:** if fastembed not available, semantic score = 0.5 (neutral), heuristics carry the weight.

---

### 4. Score Aggregator (`ghosttype/scorer.py`)

```python
WEIGHTS = {
    "heuristic": 0.55,
    "semantic":  0.45,
}

def aggregate(heuristic_score: float, semantic_score: float) -> int:
    raw = WEIGHTS["heuristic"] * heuristic_score + WEIGHTS["semantic"] * semantic_score
    return round(raw * 100)
```

Passage-level scores → document score = weighted average (longer passages count more).

---

### 5. Rewrite Engine (`ghosttype/rewriter.py`) — LLM mode only

**Responsibility:** suggest human rewrites for flagged passages.

- Connects to Ollama via HTTP (`localhost:11434`)
- Default model: `qwen2.5:3b` (fast, good quality)
- Fallback: `phi3.5:mini`
- Prompt is minimal and directive (see `PROMPTS.md`)
- Streaming output for CLI feedback

```python
def rewrite_passage(passage: str, hits: list[PatternHit]) -> str:
    ...
```

Model is **never** called if `--no-llm` flag is set.

---

### 6. CLI (`ghosttype/cli.py`)

Built with `typer` + `rich`.

Commands:
```
ghosttype analyze <file>   [--rewrite] [--model STR] [--json] [--no-llm]
ghosttype serve            [--port INT] [--host STR]
ghosttype version
```

Exit codes:
| Code | Meaning |
|------|---------|
| 0 | Score < 40 (clean) |
| 1 | Score 40–70 (moderate) |
| 2 | Score > 70 (high slop) |

Exit codes enable shell scripting: `ghosttype analyze draft.txt || echo "too sloppy"`

---

### 7. API (`ghosttype/api.py`) — optional

FastAPI app, same pipeline as CLI.

```
POST /analyze
  body: { "text": "...", "rewrite": false }
  returns: AnalysisResult

GET  /health
GET  /version
```

---

## Data flow (--no-llm mode)

```
text.txt → Preprocessor → [Passage, Passage, ...]
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
          HeuristicEngine  SemanticScorer  (nothing else)
               │               │
               └───────┬───────┘
                        ▼
                  ScoreAggregator
                        │
                        ▼
                   AnalysisResult → rich CLI output / JSON
```

## Data flow (--llm mode)

Same as above, then:
```
AnalysisResult (passages with score > threshold)
        │
        ▼
   RewriteEngine (Ollama)
        │
        ▼
   AnalysisResult + rewrites → CLI output
```

---

## Config (`~/.config/ghosttype/config.toml`)

```toml
[scoring]
heuristic_weight = 0.55
semantic_weight  = 0.45
rewrite_threshold = 60   # only suggest rewrites for passages scoring above this

[llm]
host  = "http://localhost:11434"
model = "qwen2.5:3b"

[output]
color = true
show_matched_text = true
```

---

## Dependencies

### Core (--no-llm)
| Package | Purpose |
|---------|---------|
| `typer` | CLI |
| `rich` | Terminal formatting |
| `fastembed` | Local embeddings |
| `numpy` | Vector math |
| `tomllib` | Config parsing (stdlib Python 3.11+) |

### LLM mode
| Package | Purpose |
|---------|---------|
| `httpx` | Ollama API calls |

### Web (optional)
| Package | Purpose |
|---------|---------|
| `fastapi` | API server |
| `uvicorn` | ASGI server |

---

## Project structure

```
ghosttype/
├── ghosttype/
│   ├── __init__.py
│   ├── cli.py
│   ├── api.py
│   ├── preprocessor.py
│   ├── scorer.py
│   ├── semantic.py
│   ├── rewriter.py
│   ├── heuristics/
│   │   ├── engine.py
│   │   └── patterns/
│   │       ├── openers.py
│   │       ├── hedges.py
│   │       ├── buzzwords.py
│   │       ├── structure.py
│   │       ├── balance.py
│   │       └── transitions.py
│   └── data/
│       ├── slop_corpus.npz
│       └── human_corpus.npz
├── tests/
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── pyproject.toml
└── README.md
```
