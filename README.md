<div align="center">

# 👻 GhostType

**Detect AI-generated slop in any text. Score it 0–100. Stay 100% local.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-136%20passing-brightgreen.svg)](#testing)

</div>

---

## What is AI slop?

AI slop is text that's technically correct but stylistically hollow. Generic openers, filler hedges, buzzword clusters, over-structured paragraphs, fake balance, neutral framing. You know it when you read it. **GhostType scores it 0–100** so you can quantify it.

```
$ ghosttype analyze essay.txt
==================================================
  GhostType - AI Slop Detector v0.5.0
==================================================

  Slop Score : 73/100  ███████░░░  HIGH
  Patterns   : 8 detected
  Passages   : 3 analyzed
```

---

## Why local-first

- **No data leaves your machine.** No telemetry. No API calls. No accounts.
- The web UI runs on `127.0.0.1` and never opens an outbound socket.
- Embeddings (~130 MB BAAI/bge-small-en-v1.5) are cached locally on first run.
- Reference corpora ship as `.npz` files — no raw text, no licensing nightmare.

---

## Three ways to use it

### 🖥️ CLI

```bash
# Single file
ghosttype analyze essay.txt

# Stdin
echo "In today's rapidly evolving landscape..." | ghosttype analyze -

# A directory of essays, recursive, with a Markdown report
ghosttype analyze ./essays/ --recursive --format md > report.md

# CI gate: fail the build if any file scores above 60
ghosttype analyze ./drafts/ --threshold 60

# Per-pattern breakdown (debug calibration)
ghosttype analyze essay.txt --explain
```

### 🌐 Web UI (drag-drop)

```bash
ghosttype serve
# → open http://127.0.0.1:8080
```

A pure-black, animated drag-drop interface. Drop a `.txt` or paste your text. Score, breakdown, per-passage diagnostics, downloadable Markdown report.

### 🔌 HTTP API

```bash
ghosttype serve --port 8080

curl -X POST http://localhost:8080/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"text": "In today'"'"'s world, we leverage synergy."}'
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Version + status |
| `/api/analyze` | POST | JSON body `{text}` → full result |
| `/api/analyze-file` | POST | Multipart upload → full result |
| `/api/analyze.md` | POST | JSON body `{text}` → Markdown report |
| `/docs` | GET | OpenAPI / Swagger UI |

---

## Install

```bash
git clone https://github.com/Zertannax/ghosttype.git
cd ghosttype

# Editable install (pulls all runtime deps)
pip install -e .

# Optional: add the web UI extras
pip install fastapi "uvicorn[standard]" python-multipart
```

Or with [Poetry](https://python-poetry.org/):

```bash
poetry install                # base + dev
poetry install --with web     # add fastapi/uvicorn for `serve`
```

---

## How it works

```
   ┌──────────────┐
   │     Text     │
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ Preprocessor │   paragraph-level segmentation
   └──────┬───────┘
          ├─────────────────┬─────────────────┐
          ▼                 ▼                 ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Heuristic    │  │ Semantic     │  │ Stylistic    │
   │ engine       │  │ scorer       │  │ scorer       │
   │              │  │              │  │              │
   │ 124 regex    │  │ fastembed +  │  │ variance,    │
   │ patterns     │  │ cosine vs    │  │ neutrality,  │
   │ 11 categories│  │ ref corpora  │  │ formality    │
   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
          └─────────────────┼─────────────────┘
                            ▼
                   ┌────────────────┐
                   │   Aggregator   │   weighted mix
                   │                │   - cluster bonus
                   │                │   - BZ-05 floor
                   │                │   - human bonus
                   └───────┬────────┘
                           ▼
                       Score 0–100
```

The final score is a weighted combination of three signals:

| Signal | Weight | What it measures |
|---|---|---|
| **Heuristic** | 40 % | Pattern matches across 11 categories |
| **Semantic** | 30 % | Cosine similarity to AI vs human reference embeddings |
| **Stylistic** | 30 % | Sentence variance, neutrality, formality, punctuation density |
| Human bonus | up to −50 | Negative-severity hits (classical oratory) reduce the score |

When 3+ distinct categories cluster in one passage, scores are amplified by 1.15× (per the PATTERNS.md spec). When 2+ high-confidence AI tells (`delve`, `tapestry`, `nuanced understanding`, `multifaceted`) appear together, the passage is automatically floored at 70.

---

## Score interpretation

| Range | Label | What it means | Exit code |
|---|---|---|:---:|
| 0–20 | **Clean** | Human voice, specific, grounded | `0` |
| 21–40 | **Mild** | Some generic phrasing, mostly OK | `0` |
| 41–60 | **Moderate** | Noticeable patterns, worth reviewing | `1` |
| 61–80 | **High** | Heavy slop, rewrites recommended | `2` |
| 81–100 | **Critical** | Almost certainly AI-generated as-is | `2` |

Exit codes enable shell scripting: `ghosttype analyze draft.txt || echo "too sloppy"`.

---

## Detection categories

| Category | Patterns | Examples |
|---|---:|---|
| Generic openers | 10 | "In today's world", "It is important to note" |
| Hedge fillers | 10 | "It is worth noting", "One could argue" |
| Buzzword clusters | 16 | `delve`, `tapestry`, `synergy`, `paradigm shift` |
| Over-structure | 6 | "Firstly… Secondly… Finally…" |
| Fake balance | 4 | "On one hand… on the other hand…" |
| AI transitions | 6 | Clustered "Furthermore,", "Moreover," |
| Journalist patterns | 12 | Listicle markers, emoji formatting, classical oratory (negative severity) |
| Conversational slop | 15 | ChatGPT setup framing, fake humility |
| Academic markers | 15 | Thesis statements, literature review, passive voice |
| Technical markers | 15 | Step-by-step, configuration callouts |
| **Creative writing** | 15 | Cerulean eyes, "her heart skipped", "in that moment she knew" |
| **Total** | **124** | English-only |

---

## Examples

| Text | Score | Verdict |
|---|---:|---|
| Churchill — *"We shall fight on the beaches…"* | **0** | ✅ Clean (human-indicator bonus fires) |
| MLK — *"I have a dream…"* | **23** | ✅ Mild |
| Kennedy — *"Ask not what your country…"* | **14** | ✅ Clean |
| Recipe — *"Add eggs. Mix well. Bake 30 min."* | **26** | ✅ Mild |
| Plain Orwell-style narration | **29** | ✅ Mild |
| AI fiction — *"Their eyes met across the moonlit garden, bathed in silver light. She felt a wave of longing…"* | **63** | ❌ High |
| AI essay slop — *"In today's rapidly evolving landscape, we must leverage transformative methodologies…"* | **70** | ❌ High |

---

## Reference corpora

GhostType ships pre-built `.npz` reference embeddings (no raw text) generated from public datasets:

- **AI**: 975 passages from RAID (`llama-chat`, `mpt`) + Falcon RefinedWeb
- **Human**: 1000 passages from RAID human + Falcon human
- **Model**: `BAAI/bge-small-en-v1.5` (384-dim, ~130 MB)

See [`DATASETS.md`](DATASETS.md) for sources, licenses, and how to rebuild your own.

---

## Benchmarking

A reproducible benchmark harness ships with the repo:

```bash
python scripts/benchmark.py --n 50 --threshold 50 --output bench.csv
```

Outputs precision / recall / F1 / accuracy at the chosen threshold. Useful for tuning thresholds against your own corpus.

---

## Development

```bash
# Run the test suite
pytest

# Lint and format
ruff check .
ruff format .

# Type check
mypy ghosttype/

# Generate a fresh AI corpus via Ollama (optional)
python scripts/generate_ai_corpus.py --model qwen3:14b \
       --output data/datasets/ollama_qwen3_14b/ --count 1000
```

The full suite runs in under 3 seconds (no fastembed required for tests — they use the keyword fallback path).

---

## Project structure

```
ghosttype/
├── ghosttype/
│   ├── cli.py              # typer CLI (analyze, serve, version)
│   ├── api.py              # FastAPI app
│   ├── pipeline.py         # shared analysis pipeline
│   ├── preprocessor.py     # paragraph segmentation
│   ├── scorer.py           # weighted aggregation + cluster/BZ-05 rules
│   ├── semantic.py         # fastembed cosine scorer (top-k, NaN-safe)
│   ├── stylistic.py        # variance, neutrality, formality
│   ├── heuristics/
│   │   ├── engine.py       # regex orchestration + dedup
│   │   └── patterns/       # 125+ patterns, one file per category
│   ├── data/               # shipped .npz reference corpora
│   └── web/                # static HTML/CSS/JS for the web UI
├── scripts/
│   ├── benchmark.py        # precision/recall/F1 harness
│   ├── build_corpus.py     # rebuild .npz from raw datasets
│   ├── download_*.py       # dataset downloaders
│   └── generate_ai_corpus.py  # generate AI samples via Ollama
├── tests/                  # 136 tests, all passing
├── ARCHITECTURE.md
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
└── CHANGELOG.md
```

---

## Limitations

- **English only.** French support is explicitly deferred.
- **Calibrated for current models.** As LLMs evolve, patterns will need updates. The benchmark harness is your friend.
- **Heuristics are conservative by design.** Precision is prioritised over recall — false positives on human prose are worse than missing some AI text.
- **No browser extension** with server-side processing. Privacy-incompatible by design.

---

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for upcoming features. Highlights:

- Extended corpus (2000 AI + 1000 human via Ollama)
- Pre-commit hook integration
- VS Code extension
- Plugin system for custom pattern packs

---

## License

MIT — see [LICENSE](LICENSE).
