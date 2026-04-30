# GhostType — Roadmap

> Long-term vision and planned milestones.

---

## v0.5.0 — Extended Corpus & Creative Detection

- [ ] Generate 1000 additional AI passages via local LLM (Ollama + Phi-3)
- [ ] Extend corpus to ~2000 AI + 1000 human embeddings
- [ ] Creative writing patterns (fiction/storytelling AI): 15 patterns
- [ ] Batch processing: analyze directories, globs, recursive
- [ ] Multiple export formats: JSON, CSV, Markdown
- [ ] Benchmark validation suite (50 AI + 50 human test texts)
- [ ] Progress bar for multi-file analysis

---

## v0.6.0 — CLI Polish & Integrations

- [ ] `--explain` flag: per-pattern rationale output
- [ ] `--threshold` flag: custom score thresholds
- [ ] Pre-commit hook integration
- [ ] VS Code extension (simple, calls CLI under the hood)
- [ ] Performance optimization: caching, lazy loading

---

## v0.7.0 — API & Web UI

- [ ] `ghosttype serve` — FastAPI server
- [ ] Web UI for interactive analysis
- [ ] OpenAPI spec
- [ ] Docker image

---

## v1.0.0 — Stable

- [ ] Corpus update pipeline documented and automated
- [ ] Published benchmarks (precision, recall, false positive rate)
- [ ] Plugin system for custom pattern packs
- [ ] Multilingual support (if demand exists)
- [ ] Homebrew formula

---

## Explicitly out of scope

- Training a classifier from scratch — heuristics + embeddings are more explainable
- Browser extension with server-side processing — privacy concern
- Paid tier / SaaS — stays open-source
- "AI content percentage" claims for SEO — not our problem
- French language support — deferred indefinitely (English-only focus)
