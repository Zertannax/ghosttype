# GhostType - Agent Instructions

> Spec vivante. Mettre a jour a chaque phase majeure. Derniere revue : init.

## Contexte Projet

Detecteur de "AI slop" (texte IA generique). Pipeline : texte → segmentation → heuristiques + embeddings → score 0-100 → rewrites optionnels (LLM local).

- **Phase actuelle** : v0.1.0 MVP (specification → code)
- **Contrainte utilisateur** : repo prive, local-first, pas de tokens hardcodes, pas de donnees perso dans le repo
- **Stack validee** : Python 3.11+, Poetry, typer, rich, fastembed

## Stack Technique

| Outil | Role | Commande cle |
|-------|------|--------------|
| Poetry | Gestion dependances + env virtuel | `poetry install` |
| Ruff | Lint + format (remplace black/flake8) | `poetry run ruff check .` / `poetry run ruff format .` |
| mypy | Type checking | `poetry run mypy ghosttype/` |
| pytest | Tests | `poetry run pytest` |
| typer | CLI framework | Deja dans pyproject.toml |
| rich | Terminal UI | Deja dans pyproject.toml |
| fastembed | Embeddings locaux | Deja dans pyproject.toml |

## Architecture (rappel)

```
Input → Preprocessor → HeuristicEngine ─┬─→ ScoreAggregator → Report (CLI/JSON/API)
                                        │
                                        └── SemanticScorer ───┘
                                        │
                                        └── [Optionnel] RewriteEngine (Ollama)
```

Modules principaux : `ghosttype/preprocessor.py`, `ghosttype/heuristics/`, `ghosttype/semantic.py`, `ghosttype/scorer.py`, `ghosttype/rewriter.py`, `ghosttype/cli.py`, `ghosttype/api.py`.

Voir [`ARCHITECTURE.md`](ARCHITECTURE.md) pour le detail complet.

## Conventions de Code

- **Python 3.11+** minimum (utiliser `tomllib` du stdlib, pas `toml`)
- **Typing strict** : tous les modeles de donnees en `@dataclass`, pas de `Any` sauf justification
- **Pattern IDs** : suivre le format `CATEGORY-##` (ex: `OP-01`, `HE-03`)
- **Fichiers de donnees** : embeddings en `.npz`, jamais de texte brut (licence Reddit)
- **CLI** : `typer` avec commandes explicites, `rich` pour le rendu
- **Tests** : un fichier `tests/test_<module>.py` par module, fixtures dans `tests/fixtures/`

## Workflow Developpement

Ordre obligatoire avant commit :
1. `poetry run ruff check .`
2. `poetry run ruff format .`
3. `poetry run mypy ghosttype/`
4. `poetry run pytest`

## Commandes Courantes

```bash
# Setup
poetry install

# Run CLI local
poetry run ghosttype analyze text.txt

# Mode offline (defaut)
poetry run ghosttype analyze text.txt --no-llm

# Tests
poetry run pytest
poetry run pytest tests/test_heuristics.py -v

# Build corpus embeddings (dev uniquement)
poetry run python scripts/build_corpus.py

# Serveur API (optionnel)
poetry run ghosttype serve --port 8080
```

## Contraintes Critiques

- **JAMAIS** de tokens, cles API, ou chemins personnels dans le code
- **JAMAIS** de donnees utilisateur reelles dans les commits
- Core `--no-llm` doit fonctionner 100% offline (pas d'appel reseau)
- Les `.npz` (embeddings) peuvent etre versionnes, jamais le texte source
- Repo prive : ne pas exposer d'informations internes dans README public

## Structure Repertoire (prevue)

```
ghosttype/
├── ghosttype/              # Package principal
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
├── scripts/                # Utilitaires dev (build_corpus, validate_corpus)
├── tests/
│   ├── fixtures/
│   └── test_*.py
├── pyproject.toml          # Poetry config
├── README.md
├── ARCHITECTURE.md
├── PATTERNS.md
├── DATASETS.md
├── ROADMAP.md
└── GHCLI.md                # Workflow GitHub CLI
```

## Roadmap et Priorites

**v0.1.0 MVP** (ce weekend) - focus reduit vs ROADMAP initial :
- [ ] Walking skeleton : pipeline end-to-end avec mocks
- [ ] Preprocessor + HeuristicEngine (3 categories minimum)
- [ ] SemanticScorer avec .npz pre-generes
- [ ] CLI `analyze` avec rich output
- [ ] `--json` flag
- [ ] `--no-llm` par defaut
- [ ] Tests pytest basiques

**Post-MVP** :
- `--rewrite` via Ollama
- `serve` (FastAPI)
- Config file
- French support

## GHCLI et Collaboration

Voir [`GHCLI.md`](GHCLI.md) pour :
- Creation du repo prive
- Gestion des issues et milestones
- Workflow de release
- Conventions de branches

## Points d'Attention pour les Agents

- **fastembed** : premier run telecharge le modele BAAI/bge-small-en-v1.5 (~130MB). Prevoir cache ou pre-telechargement.
- **Ollama** : le rewrite engine suppose Ollama sur `localhost:11434`. Ne pas faire planter le CLI si absent (mode `--no-llm` doit toujours marcher).
- **Windows** : verifier les chemins (le dev principal est sur Windows). Utiliser `pathlib` partout.
- **Embeddings** : les fichiers `.npz` doivent etre generes via `scripts/build_corpus.py` avant de pouvoir tester le semantic scorer.
- **Licences datasets** : on ship uniquement des embeddings, jamais de texte brut (contrainte legale Reddit).

## Questions en Suspens

- Hosting du repo : prive GitHub (a creer via GHCLI)
- CI/CD : pas pour v0.1.0, prevoir GitHub Actions post-MVP
- Packaging PyPI : post-v1.0

---

*Document vivant - a mettre a jour apres chaque phase majeure.*
