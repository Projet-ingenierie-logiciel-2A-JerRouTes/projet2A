# Guide : Pré-commit Python + Markdown

Ce document explique les différentes étapes pour configurer le hook `pre-commit` de notre projet, afin de formater automatiquement les fichiers Python et Markdown avant chaque commit.

______________________________________________________________________

## 1️⃣ Installation des outils nécessaires

### Python / Ruff

Ruff est utilisé pour le **formatage et le linting des fichiers Python**.

```bash
# Installer Ruff via pip
pip install ruff

# Installer mdformat via pip
pip install mdformat
```

Contenu du fichier pre-commit

```bash
#!/bin/bash
set -e

echo "=== Hook pre-commit ==="

# Fichiers Python uniquement
STAGED_PY=$(git diff --cached --name-only --diff-filter=d | grep '\.py$' || true)

# Fichiers Markdown uniquement
STAGED_MD=$(git diff --cached --name-only --diff-filter=d | grep '\.md$' || true)

echo "Fichiers Python analysés : $STAGED_PY"
echo "Fichiers Markdown analysés : $STAGED_MD"
echo

# Formatage Python
if [ -n "$STAGED_PY" ]; then
    echo "[1/2] Formatage automatique Python (Ruff)"
    ruff format $STAGED_PY || { echo "Erreur de format Python"; exit 1; }
    echo "[2/2] Corrections automatiques Python (Ruff check)"
    ruff check --fix $STAGED_PY || { echo "Erreurs Python à corriger"; exit 1; }
fi
echo

# Formatage Markdown
if [ -n "$STAGED_MD" ]; then
    echo "[3/3] Formatage automatique Markdown (mdformat)"
    mdformat $STAGED_MD || { echo "Erreur de format Markdown"; exit 1; }
fi
echo

# Mise à jour du staging
git add $STAGED_PY $STAGED_MD
echo "Mise à jour du staging terminée"

echo "Toutes les vérifications sont passées."
echo "Commit autorisé."
exit 0
```

Rendre le pre-commit executable

```bash
chmod +x .git/hooks/pre-commit
```
