# Guide : Automatisation du linting et du formatage (Python / Markdown)

Ce document explique les différentes étapes pour configurer le hook `pre-commit` du projet, afin de formater automatiquement les fichiers Python et Markdown avant chaque commit.

______________________________________________________________________

## Installation des outils nécessaires

Pour ajouter d’autres éléments de linting ou de formatage, il est nécessaire d’installer les outils correspondants.

### Python

Ruff est utilisé pour le **linting et le formatage des fichiers Python**.\
La configuration de Ruff est définie dans le fichier `ruff.toml` à la racine du projet.

```bash
# Installer Ruff via pip
pip install ruff
```

### Markdown

Le formatage des fichiers Markdown est réalisé avec mdformat.

```bash
# Installer mdformat via pip
pip install mdformat
```

______________________________________________________________________

## Créeation du hook pre-commit

Utiliser la commande suivante pour créer ou modifier le fichier pre-commit :

```bash
nano .git/hooks/pre-commit

# Pour sauvegarder et sortir Ctrl + X puis O(Oui)
```

Contenu du fichier pre-commit dans le dossier .git/hooks.

```bash
#!/bin/bash
set -e

echo "=== Hook pre-commit ==="

# =============================================
# Étape 1 - Désignation des éléments à vérifier
# =============================================

# Fichiers Python uniquement
STAGED_PY=$(git diff --cached --name-only --diff-filter=d | grep '\.py$' || true)

# Fichiers Markdown uniquement
STAGED_MD=$(git diff --cached --name-only --diff-filter=d | grep '\.md$' || true)

echo "Fichiers Python analysés : $STAGED_PY"
echo "Fichiers Markdown analysés : $STAGED_MD"
echo

# =============================================
# Étape 2 - Routine Python
# =============================================
if [ -n "$STAGED_PY" ]; then
    echo "[1/2] Formatage automatique Python (Ruff)"
    ruff format $STAGED_PY || { echo "Erreur de format Python"; exit 1; }
    echo "[2/2] Corrections automatiques Python (Ruff check)"
    ruff check --fix $STAGED_PY || { echo "Erreurs Python à corriger"; exit 1; }
fi
echo

# =============================================
# Étape 3 - Routine Markdown
# =============================================
if [ -n "$STAGED_MD" ]; then
    echo "[3/3] Formatage automatique Markdown (mdformat)"
    mdformat $STAGED_MD || { echo "Erreur de format Markdown"; exit 1; }
fi
echo

# =============================================
# Étape 4 - Mise à jour du staging
# =============================================
git add $STAGED_PY $STAGED_MD
echo "Mise à jour du staging terminée"

echo "Toutes les vérifications sont passées."
echo "Commit autorisé."
exit 0
```

Rendre le hooks pre-commit executable

```bash
chmod +x .git/hooks/pre-commit
```

______________________________________________________________________

## Remarque

### Pour information : utilisation des lintage et formatage en ligne de commande

#### Python

Le linting et le formatage du code Python sont réalisés avec **Ruff**.

- Applique automatiquement :
  - conventions PEP 8
  - tri et organisation des imports
  - correction des erreurs simples et du style du code

*Rappel* : La configuration de Ruff est définie dans le fichier `ruff.toml` à la racine du projet.

**Linting**
Analyser le code et afficher les problèmes détectés :

```bash
uv run ruff check
```

Corriger automatiquement les problèmes simples :

```bash
uv run ruff check --fix
```

**Formatage**
Vérifier que le code respecte les règles de formatage :

```bash
uv run ruff format --check
```

Appliquer le formatage automatique :

```bash
uv run ruff format
```

#### Markdown

Le formatage des fichiers Markdown est réalisé avec **mdformat**.

- Corrige automatiquement :
  - espaces en fin de ligne
  - longueur de ligne
  - saut de ligne final
  - indentation cohérente

**Vérifier le formatage (lintage)**

```bash
mdformat --check README.md
```

**Effectuer le formatage**

```bash
mdformat README.md
```
