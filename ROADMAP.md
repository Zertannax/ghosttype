# GhostType — Roadmap

> Long-term vision and planned milestones.

---

## ✅ v0.5.0 — Web UI, batch CLI, expanded corpus *(released 2026-05-02)*

- [x] Generate 1000 additional AI passages via local LLM (Ollama + qwen3:14b)
- [x] Extend corpus to ~2000 AI + 1000 human embeddings
- [x] Creative writing patterns (fiction/storytelling AI): 15 patterns (CR-01 to CR-15)
- [x] Batch processing: analyze directories, globs, recursive
- [x] Multiple export formats: JSON, CSV, Markdown
- [x] Benchmark validation suite (`scripts/benchmark.py`)
- [x] Progress bar for multi-file analysis
- [x] Local web UI (`ghosttype serve`) with drag-drop and animations
- [x] HTTP API (`/api/analyze`, `/api/analyze-file`, `/api/analyze.md`)
- [x] `--explain` flag with per-component score breakdown
- [x] `--threshold N` flag for CI gates
- [x] `--quiet` flag for shell scripting
- [x] `patterns list` / `patterns describe` subcommands
- [x] Public release on GitHub (MIT licensed)

**Benchmark at v0.5.0**: F1 = 0.72, recall = 0.78 at threshold 30 (50/class, seed 42).

---

## v0.6.0 — Calibration & integrations

- [ ] Held-out benchmark split (no data leakage between corpus and test set)
- [ ] Pre-commit hook integration (`.pre-commit-hooks.yaml`)
- [ ] VS Code extension (calls the CLI under the hood)
- [ ] Config file (`~/.config/ghosttype/config.toml`) for custom weights / thresholds
- [ ] Streaming analysis on large files (process passage-by-passage without loading the whole text)
- [ ] Performance optimization: persistent embedding cache across runs

---

## v0.7.0 — Distribution

- [ ] PyPI release (`pip install ghosttype`)
- [ ] Docker image (`ghosttype/ghosttype` on Docker Hub)
- [ ] Homebrew formula
- [ ] Standalone Windows / macOS / Linux binaries (PyInstaller)
- [ ] Automated release pipeline via GitHub Actions

---

## v1.0.0 — Stable

- [ ] Plugin system for custom pattern packs
- [ ] Published benchmarks (precision, recall, F1) against multiple AI generators
- [ ] Deeper semantic detection (ensemble of cosine + perplexity from a small local LM)
- [ ] Web UI gets a passage-level "rewrite suggestion" mode (optional, behind a flag)
- [ ] Stability guarantee on the JSON output schema

---

## Explicitly out of scope

- Training a classifier from scratch — heuristics + embeddings stay more explainable
- Browser extension with server-side processing — privacy concern
- Paid tier / SaaS — stays open-source, local-first
- "AI content percentage" claims for SEO — not our problem
- French (or any non-English) language support — repo is English-only by design
