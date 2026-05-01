# GhostType — Changelog

All notable changes to GhostType.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [v0.5.0] — 2026-05-02

### Added
- **Web UI** (`ghosttype serve`): pure-black drag-drop interface served by FastAPI on `127.0.0.1`. Score count-up animation, color-coded score bar, accordion passages with auto-expand on score > 60, downloadable Markdown report. Auto-opens the browser on start.
- **HTTP API**: `POST /api/analyze`, `POST /api/analyze-file`, `POST /api/analyze.md`, `GET /api/health`. OpenAPI docs at `/docs`.
- **Batch processing** in CLI: `analyze` accepts files, directories, glob patterns. New `--recursive`, `--ext` flags. Rich progress bar + summary table for multi-file runs.
- **Multiple output formats**: `--format rich|json|csv|md`. CSV/MD piped reports.
- **`--explain` flag**: shows score breakdown table (heuristic / semantic / stylistic / human bonus) and per-passage rule indicators (cluster bonus, BZ-05 floor) with pattern descriptions.
- **`--threshold N` flag**: binary CI gate (score > N → exit 2, else exit 0).
- **`--quiet` flag**: prints only the integer score (single file) or `<score>\t<path>` lines (batch). Useful for shell scripting.
- **`patterns list` / `patterns describe`** subcommands: discover all 124 patterns, show regex / severity / description per pattern.
- **Creative writing patterns** (15 patterns, CR-01 to CR-15): cliché openers, purple prose, told-not-shown emotion, generic body-action beats, eye-contact clichés, AI landscape descriptors, storybook resolutions, body-horror cliché bundles.
- **Clustering bonus**: passage score multiplied by 1.15× when 3+ distinct positive-severity categories appear together (PATTERNS.md spec).
- **BZ-05 special rule**: 2+ high-confidence AI tells (delve / tapestry / nuanced understanding / multifaceted) floor a passage at score 70.
- **Top-k semantic similarity**: `_topk_mean(k=10)` instead of flat mean over the full corpus.
- **Corpus expansion**: 2000 AI passages (893 RAID + 1107 Ollama qwen3:14b + qwen2.5:3b) + 1000 human (500 RAID + 500 Falcon).
- **Benchmark harness** (`scripts/benchmark.py`): precision / recall / F1 / accuracy at configurable threshold.
- **Polished public README** with banner, logo, and live screenshots.
- **MIT LICENSE** file.

### Changed
- **Pipeline refactor**: shared `ghosttype/pipeline.py` used by both CLI and API for a single source of truth.
- **Heuristic engine**: now deduplicates overlapping hits at the same start position (kept strongest signal). `re.MULTILINE` enabled so `^`-anchored patterns actually match.
- **Score normalization**: passage scores normalized by word count instead of character count (fairer for short passages).
- **Exit code alignment**: 3-bucket exit code now matches SCORE_LABELS buckets (61–70 = High → exit 2, was MODERATE before).
- **Classical-oratory negative-severity patterns** (JR-21, JR-23, JR-24) rewritten in English so the human-indicator bonus actually fires on Churchill / MLK / Kennedy-style prose.
- **Mode offline**: `semantic.py` falls back to keyword scoring when fastembed is unavailable OR when reference corpora are missing. Cosine similarity is now NaN-safe.
- **Fastembed model and corpora cached at module level** (was reloaded on every call).
- **Calibration recap**: at threshold=30 against the v0.5.0 corpus, F1 rises from **0.59 → 0.72** (recall 0.60 → 0.78). Note: benchmark and corpus share data sources; a held-out evaluation is on the roadmap.

### Removed
- **French language support**: 3 pattern files (`french_*.py`), `test_french.py`, `JR-01/03/05/07/09/11..19/22`, FR markers in `stylistic.py` and `semantic.py` keyword fallback. Per ROADMAP, English-only focus.
- **Internal dev notes** (`AGENTS.md`, `GHCLI.md`) — replaced by the public README.

### Fixed
- **`re.MULTILINE` missing**: ST-04, HE-05, JR-27 anchored patterns previously never matched in practice.
- **Mojibake** in CLI output (`â–ˆ`, `âœ"`) → clean UTF-8 (`█`, `✓`).
- **Fake-green tests**: 7 tests that passed regardless of code behavior replaced with real assertions.
- **JR-12** no longer matches every `80%` in English text (now requires FR article context).
- **JR-13** broadened to catch 3rd-group verb participles and feminine forms.
- **`generate_ai_corpus.py`** prompt cap: oversampling now produces the full requested count (was capped at 100 = pool size). Resume logic updated to track per-prompt occurrences.
- **Many false-positive patterns** tightened: AC-04 (`however`/`therefore`), AC-12 (`complex`), AC-14 (`while`), TC-07 (`important`), BZ-08 (`framework`/`landscape`), CS-14 (`process`/`journey`), and others now require multi-word context.

---

## [v0.4.2] — 2026-05-01

### Added
- **Academic patterns** (15 patterns, AC-01 to AC-15): thesis statements, findings presentation, literature review markers, transition phrases, conclusion patterns, significance claims, passive voice overuse, methodology hedging, scope declarations, limitation framing, citation clustering, syntactic complexity, emphasis chains, comparative analysis, synthesis signals
- **Technical patterns** (15 patterns, TC-01 to TC-15): section introductions, step-by-step procedures, concrete examples, prerequisites, command blocks, visual references, callout boxes, conclusion/next steps, benefit statements, configuration examples, implementation notes, troubleshooting steps, performance metrics, verification checks
- Updated pattern registry to include academic and technical modules

### Changed
- Total pattern count: ~110 across 10 active categories

---

## [v0.4.1] — 2026-04-30

### Added
- **Conversational slop patterns** (15 patterns, CS-01 to CS-15): setup framing, simplification claims, evolution announcements, generalization markers, fake humility, accumulation phrases, practice disclaimers, balance hedging, ultimate summary, adaptation hedging, help offers, neutrality signals, clarity hedging, journey metaphors, value statements
- **Enhanced stylistic scoring**: paragraph variance detection (AI = uniform ~50-70 word paragraphs) + neutrality score (AI avoids strong opinions)
- **Human indicator bonus refinement**: improved detection of classical oratory (Churchill, MLK, Socrates) with negative severity patterns (-5 to -50 point reduction)

### Fixed
- ChatGPT conversational text now scores 64/100 HIGH (was 36/100 MILD false negative)
- Stylistic scorer now catches paragraph-level uniformity

### Changed
- Score weights: heuristic 40%, semantic 30%, stylistic 30% (was 55%/45%)
- Total pattern count: ~80

---

## [v0.4.0] — 2026-04-30

### Added
- **Robust English corpus**: 975 AI + 1000 human embeddings (384-dim, BAAI/bge-small-en-v1.5)
  - Sources: RAID (llama-chat, mpt AI) + RAID (human) + Falcon RefinedWeb (human)
  - Quality filters: 50-300 word passages, deduplication, balance sampling
- **Corpus build scripts**:
  - `scripts/download_datasets.py` — download RAID from HuggingFace
  - `scripts/download_falcon.py` — download Falcon RefinedWeb sample
  - `scripts/build_corpus.py` — filter, dedup, sample, embed with batch processing
- **Corpus metadata**: `corpus_meta.json` tracking sources, models, dates
- **Batch embedding**: size 32 to avoid ONNXRuntime OOM on Windows

### Changed
- Semantic scorer now uses pre-built `.npz` corpora instead of runtime embedding
- Model: BAAI/bge-small-en-v1.5 (~130MB download on first run)

---

## [v0.3.0] — 2026-04-29

### Added
- **Stylistic scoring** module: sentence length variance, word length, punctuation density, rare/formal word ratios
- **27 journalist patterns** (incl. 7 new): conventional phrases, unsupported claims, accumulation, balance, quotes framing
- **Human indicator bonus system**: negative severity patterns (-0.5 to -1.0) for classical oratory detection (Churchill, MLK, Socrates) and genuine human emotion
- **French patterns** (deferred): basic opener/hedge/buzzword patterns for future `fr` support

### Fixed
- Windows UnicodeEncodeError: replaced box-drawing chars (━/█/░) with ASCII (=/█/░)
- Score aggregation: human indicators reduce score instead of always increasing

### Changed
- Score weights: heuristic 55%, semantic 45%
- Exit codes: 0 (<40), 1 (40-70), 2 (>70)

---

## [v0.2.0] — 2026-04-28

### Added
- **Semantic scorer** (fastembed, BAAI/bge-small-en-v1.5)
- **Initial reference corpus** (~500 passages each from HC3 + RAID)
- **JSON output** (`--json` flag)
- **Exit codes** for shell scripting
- `--version` command

### Changed
- Architecture: preprocessor → heuristic engine → semantic scorer → aggregator

---

## [v0.1.0] — 2026-04-26

### Added
- Initial CLI with typer + rich
- Preprocessor (paragraph segmentation)
- Heuristic engine with 30 patterns across 6 categories:
  - Generic openers (5)
  - Hedge fillers (5)
  - Buzzword clusters (5)
  - Over-structure (5)
  - Fake balance (4)
  - AI transitions (4)
- Score aggregator (0-100)
- Rich terminal output
- MIT license

---

## Planned

See [ROADMAP.md](ROADMAP.md) for upcoming features.
