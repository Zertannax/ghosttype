# GhostType — Roadmap

---

## v0.1.0 — Hackathon MVP (ce weekend)

**Goal:** Working CLI, publishable on GitHub, demo GIF ready.

### Must have
- [ ] Preprocessor (paragraph segmentation)
- [ ] Heuristic engine (all 6 categories, ~30 patterns)
- [ ] Semantic scorer (fastembed + pre-built .npz corpus)
- [ ] Score aggregator
- [ ] CLI: `ghosttype analyze <file>` with rich output
- [ ] `--json` flag for piping
- [ ] `--no-llm` mode (default)
- [ ] README with demo GIF (asciinema)
- [ ] MIT license
- [ ] `pyproject.toml` with proper metadata

### Nice to have (if time allows)
- [ ] `--rewrite` flag via Ollama
- [ ] Exit codes for shell scripting
- [ ] `ghosttype serve` (FastAPI)
- [ ] Config file support (`~/.config/ghosttype/config.toml`)

---

## v0.2.0 — Post-hackathon polish

- [ ] French language support (`--lang fr`) using AuTextification corpus
- [ ] Per-pattern explainability output (`--explain`)
- [ ] Batch mode: analyze entire directories
- [ ] Pre-commit hook integration
- [ ] VS Code extension (simple, calls CLI under the hood)
- [ ] Homebrew formula

---

## v0.3.0 — Rewrite engine maturity

- [ ] Multiple rewrite styles (academic → casual, formal → punchy)
- [ ] Diff view: original vs rewrite side by side
- [ ] Accept/reject rewrites interactively in TUI
- [ ] OpenAI/Anthropic API support as alternative to Ollama

---

## v1.0.0 — Stable

- [ ] Corpus update pipeline documented and automated
- [ ] Benchmarks published (accuracy on HC3, RAID)
- [ ] Multilingual: EN, FR, DE
- [ ] Plugin system for custom pattern packs
- [ ] Web UI polished and documented

---

## Explicitly out of scope (forever)

- Training a classifier from scratch — heuristics + embeddings are good enough and more explainable
- Browser extension with server-side processing — privacy concern
- Paid tier / SaaS — this stays open-source
- "AI content percentage" claims for SEO purposes — not our problem to solve

---

## Hackathon timeline

| Time | Task |
|------|------|
| Vendredi soir 21h | Init repo, pyproject.toml, module skeleton |
| Vendredi soir 22h–00h | Heuristic engine: openers + hedges + buzzwords |
| Samedi matin 9h–12h | Semantic scorer + corpus .npz build script |
| Samedi 12h–14h | Score aggregator + CLI rich output |
| Samedi 14h–16h | Tests, edge cases, --json flag |
| Samedi soir | Rave. Ne pas coder. |
| Dimanche 10h–13h | --rewrite via Ollama (si motivé) |
| Dimanche 13h–16h | README final, asciinema demo, release v0.1.0 |
| Dimanche 16h | Push. Done. |
