# GhostType — Architecture

## Overview

GhostType analyzes text in three layers — heuristic, semantic, stylistic — and combines their signals into a single 0–100 score. The same pipeline backs the CLI, the HTTP API, and the web UI.

```
Input (file / stdin / glob / directory / web upload)
        │
        ▼
┌───────────────────┐
│   Preprocessor    │  paragraph-level segmentation, HTML stripping
└────────┬──────────┘
         │
         ▼
┌───────────────────┐  ┌────────────────────┐  ┌──────────────────────┐
│ Heuristic engine  │  │  Semantic scorer   │  │  Stylistic scorer    │
│ 124 regex / 11 cat│  │  fastembed cosine  │  │  variance, neutrality│
│ + dedup + rules   │  │  vs ref corpora    │  │  formality, density  │
└────────┬──────────┘  └─────────┬──────────┘  └─────────┬────────────┘
         └─────────────────────┼─────────────────────────┘
                               ▼
                  ┌──────────────────────┐
                  │   Score aggregator   │  weighted mix
                  │                      │  + cluster bonus (×1.15)
                  │                      │  + BZ-05 floor (≥70)
                  │                      │  + human-indicator bonus
                  └──────────┬───────────┘
                             ▼
                       AnalysisResult
                       (score 0–100,
                        breakdown, hits)
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  Rich console       JSON / CSV / MD          Web UI render
  (CLI default)      (CLI / API endpoints)    (animated, dark)
```

---

## Modules

### `ghosttype/pipeline.py`

Single source of truth for the analysis flow. Both the CLI and the API call:

```python
from ghosttype.pipeline import analyze_text, result_to_dict

result = analyze_text(text)            # AnalysisResult | None
payload = result_to_dict(result)       # JSON-serializable dict
```

`analyze_text` orchestrates: preprocess → heuristic engine → semantic scorer → stylistic scorer → aggregator. Returns `None` for whitespace-only input.

---

### `ghosttype/preprocessor.py`

Splits text into `Passage` dataclasses (`index`, `text`, `start_char`, `end_char`). Strategy:

- Strip basic HTML tags and named entities (`&amp;`, `&lt;`, `&gt;`)
- Split on double newlines (`\n\s*\n`)
- Fall back to sentence segmentation if no paragraphs are found

---

### `ghosttype/heuristics/`

Regex-based pattern detection.

```
heuristics/
├── engine.py       — orchestrates patterns, dedupes overlapping hits
└── patterns/
    ├── openers.py        (10 OP-XX)
    ├── hedges.py         (10 HE-XX)
    ├── buzzwords.py      (16 BZ-XX, incl. BZ-05 high-confidence tells)
    ├── structure.py      (6  ST-XX)
    ├── balance.py        (4  FB-XX)
    ├── transitions.py    (6  TR-XX)
    ├── journalist.py     (12 JR-XX, incl. negative-severity oratory)
    ├── conversational.py (15 CS-XX)
    ├── academic.py       (15 AC-XX)
    ├── technical.py      (15 TC-XX)
    └── creative.py       (15 CR-XX, fiction / storytelling)
```

Each pattern is a dict:

```python
{
    "id": "BZ-05",
    "category": "buzzword",
    "regex": r"\bdelve\b|\btapestry\b|\bnuanced understanding\b|\bmultifaceted\b",
    "severity": 0.9,           # negative = human indicator
    "description": "AI self-description buzzword (high confidence)",
}
```

The engine compiles every regex with `re.IGNORECASE | re.MULTILINE` and deduplicates hits sharing the same `(matched_text, start_char)` — keeps the strongest absolute severity. This prevents triple-counting when the same phrase appears in multiple categories (e.g. "in summary" in ST-04 + AC-05 + TC-08).

---

### `ghosttype/semantic.py`

fastembed cosine similarity against pre-built reference corpora.

- Model: `BAAI/bge-small-en-v1.5` (384-dim, ~130 MB, cached at module level)
- Reference corpora: `slop_corpus.npz` (2000 vectors) and `human_corpus.npz` (1000 vectors)
- Per-passage score: `top_k_mean(sim_to_slop) / (top_k_mean(sim_to_slop) + top_k_mean(sim_to_human))` with `k = 10`
- NaN-safe: zero-norm rows produce 0.0, never NaN
- Validated on load: shape must be `(n, 384)`, otherwise the corpus is ignored with a warning
- Falls back to a keyword-based heuristic when fastembed is unavailable OR when corpora are missing

---

### `ghosttype/stylistic.py`

Statistical text features. Each feature is normalized to `[0, 1]` and then combined.

| Feature | Weight | Higher = |
|---|---:|---|
| Sentence-length variance | 0.20 | More uniform → AI-like (skipped on short-form ≤30 char/sentence) |
| Paragraph-length variance | 0.25 | More uniform → AI-like (skipped if ≤20 words/paragraph) |
| Average word length | 0.10 | Longer words → AI-like |
| Punctuation density | 0.10 | Higher → AI-like |
| Common-word ratio | 0.15 | More common words → AI-like |
| Formal-marker ratio | 0.10 | More "furthermore"/"nevertheless"/etc. |
| Neutrality | 0.10 | Fewer emotional words → AI-like |

The two variance signals are deliberately disabled on recipes / bullet lists / instruction text where short uniform sentences are the natural form.

---

### `ghosttype/scorer.py`

Combines the three signals into the final document score.

```python
WEIGHTS = {"heuristic": 0.40, "semantic": 0.30, "stylistic": 0.30}
```

Per-passage score:

```python
total_severity = sum(hit.severity for hit in hits)
length_factor  = sqrt(max(10, word_count)) / 3.0
score          = (total_severity / length_factor) * 100
if 3+ distinct positive categories cluster:  score *= 1.15   # cluster bonus
if 2+ BZ-05 hits in passage:                 score = max(score, 70)
```

Document score: length-weighted mean of passage scores, blended with semantic and stylistic, then adjusted by the human-indicator bonus (negative-severity hits like classical oratory reduce the score by up to −50).

```python
@dataclass
class AnalysisResult:
    score: int                     # 0–100
    label: str                     # Clean / Mild / Moderate / High / Critical
    passages: list[PassageResult]
    total_hits: int
    exit_code: int                 # 0 / 1 / 2
    breakdown: ScoreBreakdown      # per-component breakdown for --explain
```

---

### `ghosttype/cli.py`

Typer-based CLI.

```
ghosttype analyze <target>   # file / dir / glob / -
                  [--format rich|json|csv|md] [--json]
                  [--recursive] [--ext txt,md]
                  [--explain] [--threshold N] [--quiet]
ghosttype serve   [--host 127.0.0.1] [--port 8080] [--no-browser]
ghosttype patterns list [--category buzzword]
ghosttype patterns describe <ID>
ghosttype version
```

Exit codes (default 3-bucket):

| Code | Meaning |
|---|---|
| 0 | Score ≤ 40 (Clean / Mild) |
| 1 | Score 41–60 (Moderate) |
| 2 | Score ≥ 61 (High / Critical) |

`--threshold N` overrides this with binary semantics: `score > N` → exit 2, otherwise exit 0.

---

### `ghosttype/api.py`

FastAPI app. Same pipeline as the CLI, served over HTTP.

```
GET  /                  static HTML UI
GET  /static/{path}     CSS / JS / logo
GET  /api/health        { status, version }
POST /api/analyze       { text } → AnalysisResult dict
POST /api/analyze-file  multipart upload → AnalysisResult dict
POST /api/analyze.md    { text } → Markdown report (text/plain)
GET  /favicon.ico       PNG logo or SVG fallback
GET  /docs              OpenAPI / Swagger UI
```

Bound to `127.0.0.1` by default. No outbound network calls. No telemetry.

---

### `ghosttype/web/`

Vanilla HTML / CSS / JS (no build step, no CDN, no webfont).

- `index.html` — single page with drag-drop zone + textarea + result panel
- `style.css` — pure `#000` background, score-driven accent colors, animations
- `app.js` — drop handler, paste, fetch to `/api/analyze`, render with auto-expand for problematic passages

Every visual asset (favicon, logo) is served from this directory.

---

## Data flow (offline mode, no fastembed)

```
text → preprocess → [Passage, ...]
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  HeuristicEngine  keyword_fallback  StylisticScorer
       │               │               │
       └───────┬───────┴───────────────┘
               ▼
         ScoreAggregator
               │
               ▼
         AnalysisResult
```

The keyword fallback in `semantic.py` produces a coarse score from formal-marker counts and buzzword density — meaningful enough to keep the pipeline differentiated when embeddings are unavailable.

---

## Reference corpora

Shipped pre-embedded as `.npz` files in `ghosttype/data/`:

| File | Shape | Contents |
|---|---|---|
| `slop_corpus.npz` | (2000, 384) | RAID `llama-chat`/`mpt` + Ollama `qwen3:14b`/`qwen2.5:3b` |
| `human_corpus.npz` | (1000, 384) | RAID human + Falcon RefinedWeb human |
| `corpus_meta.json` | — | sources, models, version, build date |

See [`DATASETS.md`](DATASETS.md) for licenses and rebuild instructions.

---

## Dependencies

### Runtime (always)
| Package | Purpose |
|---|---|
| `typer` | CLI |
| `rich` | Terminal rendering |
| `numpy` | Vector math |

### Runtime (semantic mode)
| Package | Purpose |
|---|---|
| `fastembed` | Local embeddings (BAAI/bge-small-en-v1.5) |

### Runtime (web mode)
| Package | Purpose |
|---|---|
| `fastapi` | API server |
| `uvicorn` | ASGI server |
| `python-multipart` | File uploads |

### Development
| Package | Purpose |
|---|---|
| `pytest` | Tests |
| `ruff` | Lint + format |
| `mypy` | Type check |

---

## Project structure

```
ghosttype/
├── ghosttype/
│   ├── __init__.py            # __version__
│   ├── pipeline.py            # shared analyze_text + result_to_dict
│   ├── cli.py                 # typer commands
│   ├── api.py                 # FastAPI app
│   ├── preprocessor.py
│   ├── scorer.py
│   ├── semantic.py
│   ├── stylistic.py
│   ├── heuristics/
│   │   ├── engine.py
│   │   └── patterns/          # 11 category modules
│   ├── data/                  # shipped .npz corpora + meta
│   └── web/                   # static HTML / CSS / JS / logo
├── scripts/
│   ├── benchmark.py
│   ├── build_corpus.py
│   ├── download_*.py
│   └── generate_ai_corpus.py
├── tests/                     # 145 tests across 8 files
├── docs/                      # logo, banner, screenshots
├── README.md
├── ARCHITECTURE.md
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
├── CHANGELOG.md
└── pyproject.toml
```
