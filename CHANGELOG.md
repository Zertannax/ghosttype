# GhostType — Changelog

All notable changes to GhostType.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
