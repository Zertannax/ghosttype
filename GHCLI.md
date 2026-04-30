# GhostType - GitHub CLI Workflow

> Guide complet pour gerer le projet avec `gh` (GitHub CLI). Aucune donnee sensible ne doit etre stockee dans ce repo.

## Prerequis

- [GitHub CLI](https://cli.github.com/) installe (`gh --version`)
- Authentifie : `gh auth login`
- Git configure

## Setup Initial (une fois)

### 1. Creer le repo prive

```bash
# Dans le dossier ghosttype/
gh repo create ghosttype --private --source=. --push
```

Ou si le repo existe deja sur GitHub :

```bash
gh repo clone utilisateur/ghosttype
```

### 2. Verifier la configuration

```bash
gh repo view --json url,visibility
```

## Scripts Utilitaires

### `scripts/gh-issue-create.ps1` - Creer une issue

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Body = "",
    [string]$Label = "",
    [string]$Milestone = ""
)

$cmd = "gh issue create --title `"$Title`" --body `"$Body`""
if ($Label) { $cmd += " --label `"$Label`"" }
if ($Milestone) { $cmd += " --milestone `"$Milestone`"" }

Invoke-Expression $cmd
```

Usage :
```powershell
.\scripts\gh-issue-create.ps1 -Title "Implement preprocessor" -Label "enhancement" -Milestone "v0.1.0"
```

### `scripts/gh-milestone-create.ps1` - Creer un milestone

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Description = "",
    [string]$DueDate = ""  # Format: YYYY-MM-DD
)

$cmd = "gh api repos/{owner}/{repo}/milestones -X POST -f title=`"$Title`""
if ($Description) { $cmd += " -f description=`"$Description`"" }
if ($DueDate) { $cmd += " -f due_on=`"${DueDate}T00:00:00Z`"" }

Invoke-Expression $cmd
```

### `scripts/gh-pr-create.ps1` - Creer une PR

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    [string]$Body = "",
    [string]$Base = "main"
)

gh pr create --title "$Title" --body "$Body" --base "$Base"
```

### `scripts/gh-release-draft.ps1` - Creer une release draft

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Tag,
    [string]$Title = "",
    [string]$Notes = ""
)

$releaseTitle = if ($Title) { $Title } else { $Tag }
gh release create $Tag --title "$releaseTitle" --notes "$Notes" --draft
```

## Workflow Quotidien

### Branches

- `main` : production stable
- `dev` : integration (optionnel pour v0.1.0)
- `feature/nom-feature` : nouvelles fonctionnalites
- `fix/nom-bug` : corrections

### Creer une feature

```bash
# 1. Creer l'issue (si pas deja faite)
gh issue create --title "Add semantic scorer" --label enhancement

# 2. Creer la branche
git checkout -b feature/semantic-scorer

# 3. Coder, commit, push
git add .
git commit -m "feat: add semantic scorer with fastembed"
git push -u origin feature/semantic-scorer

# 4. Creer la PR
gh pr create --title "feat: semantic scorer" --body "Closes #123"

# 5. Merger (apres review)
gh pr merge --squash --delete-branch
```

### Lister et trier les issues

```bash
# Issues ouvertes
gh issue list --state open

# Par milestone
gh issue list --milestone v0.1.0

# Par label
gh issue list --label bug

# Voir une issue specifique
gh issue view 42
```

### Synchroniser avec le remote

```bash
# Pull les dernieres changements
git pull origin main

# Verifier le status
gh repo view --json pushedAt,defaultBranchRef
```

## Milestones & Planning

### Creer les milestones pour v0.1.0

```bash
gh api repos/{owner}/{repo}/milestones -X POST -f title="v0.1.0 MVP" -f description="Hackathon MVP - CLI core" -f due_on="2026-05-03T23:59:59Z"
```

### Assigner des issues aux milestones

```bash
gh issue edit 1 --milestone "v0.1.0 MVP"
```

### Progression

```bash
# Voir les issues par milestone
gh issue list --milestone "v0.1.0 MVP"

# Voir le pourcentage de completion
gh api repos/{owner}/{repo}/milestones | ConvertFrom-Json | Select title, open_issues, closed_issues
```

## Releases

### Process de release

```bash
# 1. S'assurer que main est propre
git checkout main
git pull origin main

# 2. Tag
gh release create v0.1.0 --title "GhostType v0.1.0" --notes-file CHANGELOG.md --draft

# 3. Publier la release (manuellement sur GitHub ou via CLI)
gh release edit v0.1.0 --draft=false
```

### Changelog

Maintenir un `CHANGELOG.md` a la racine :

```markdown
# Changelog

## [v0.1.0] - 2026-05-03
### Added
- CLI analyze avec heuristiques
- Semantic scorer (embeddings)
- Rich output
- JSON export
- Tests pytest

## [Unreleased]
### Added
- ...
```

## Securite & Contraintes

- **JAMAIS** de tokens, mots de passe, ou cles API dans les issues/PRs
- **JAMAIS** de donnees utilisateur dans les commits
- Utiliser `gh auth` pour l'authentification (stocké localement, pas dans le repo)
- Le repo est **prive** : verifier avec `gh repo view --json visibility`
- Pas de GitHub Actions pour l'instant (pas de CI/CD dans le cloud pour v0.1.0)

## Commandes de Reference

| Commande | Description |
|----------|-------------|
| `gh auth status` | Verifier l'authentification |
| `gh repo view` | Voir les infos du repo |
| `gh issue list` | Lister les issues |
| `gh issue create` | Creer une issue |
| `gh issue edit 1` | Modifier une issue |
| `gh pr list` | Lister les PRs |
| `gh pr create` | Creer une PR |
| `gh pr merge` | Merger une PR |
| `gh release create` | Creer une release |
| `gh api` | Appel API brut |

## Alias Utiles (optionnel)

Ajouter dans `~/.config/gh/config.yml` :

```yaml
aliases:
  il: issue list
  ic: issue create
  pl: pr list
  pc: pr create
  pm: pr merge
```

Usage : `gh il` au lieu de `gh issue list`

---

*Document a jour avec la version de gh installee.*
