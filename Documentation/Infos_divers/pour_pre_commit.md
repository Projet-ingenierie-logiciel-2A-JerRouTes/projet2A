# Guide : Automatisation du linting et du formatage (Python / Markdown)

Ce document explique les différentes étapes pour configurer le hook `pre-commit` du projet, afin de formater automatiquement les fichiers Python et Markdown avant chaque commit.

______________________________________________________________________

## Installation des outils nécessaires

vant de pouvoir utiliser les outils de vérification, tu dois installer les dépendances sur ta machine.

### 🐍 Backend & Documentation

Ruff est utilisé pour le **linting et le formatage des fichiers Python**.\
La configuration de Ruff est définie dans le fichier `ruff.toml` à la racine du projet.

```bash
# Installer Ruff via pip
pip install ruff mdformat
```

**Mise en place des règles de correction**

A la racine dans le fichier : `pyproject.toml`

```
[project]
name = "projet2a"
version = "0.1.0"
description = "Gestionnaire de stock"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

# =============================================
# Configuration des TESTS (Pytest)
# =============================================
[tool.pytest.ini_options]
pythonpath = ["."] # Permet à pytest de voir les modules depuis la racine
testpaths = ["src/backend/tests"] # Dossier où chercher les scripts de test

# =============================================
# Configuration du LINTER & FORMATTER (Ruff)
# =============================================
[tool.ruff]
# Indique que la racine du projet est le point de départ
src = ["."]
# Longueur de ligne maximale (équilibre entre lisibilité et écrans larges)
line-length = 88
# Cible la version spécifique de Python pour utiliser les dernières syntaxes
target-version = "py313"

[tool.ruff.lint]
# E : Erreurs de style (pycodestyle)
# F : Erreurs logiques graves (Pyflakes)
# I : Tri automatique des imports (Isort)
# W : Avertissements de style (Warnings)
select = ["E", "F", "I", "W"]

# Dossiers à ignorer par le linter (fichiers générés ou virtuels)
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "build",
]

[tool.ruff.format]
# Utilisation de guillemets doubles (standard Python moderne)
quote-style = "double"
# Indentation par espaces (standard PEP 8)
indent-style = "space"
```

### ⚛️ Frontend & Styles

Depuis le dossier racine, installe les outils Node.js avec cette commande (elle évite les conflits de versions entre ESLint 9 et 10) :

```bash
npm install --save-dev eslint prettier stylelint stylelint-config-standard globals @eslint/js eslint-plugin-react --legacy-peer-deps
```

**Mise en place des règles de correction**

**Pour le react**
Dans le fichier src/frontend/src/ : `eslint.config`

```
// 1. IMPORTATION DES PLUGINS ET OUTILS
import js from "@eslint/js"; // Importe les règles recommandées par défaut pour JavaScript
import reactPlugin from "eslint-plugin-react"; // Importe les fonctionnalités spécifiques à l'analyse de React
import globals from "globals"; // Bibliothèque pour reconnaître les variables globales (window, document, etc.)

export default [
  // 2. CONFIGURATION DE BASE
  js.configs.recommended, // Active les règles de base (ex: éviter les boucles infinies, variables non définies)

  {
    // 3. CIBLAGE DES FICHIERS
    // Indique que ces règles s'appliquent à tous les fichiers JS, JSX et TypeScript
    files: ["**/*.{js,jsx,ts,tsx}"],

    // 4. ACTIVATION DU PLUGIN REACT
    plugins: {
      react: reactPlugin,
    },

    // 5. OPTIONS DE LANGAGE ET ENVIRONNEMENT
    languageOptions: {
      parserOptions: {
        ecmaFeatures: {
          jsx: true, // Autorise le linter à lire la syntaxe JSX (HTML dans le JS)
        },
      },
      globals: {
        // Ajoute les variables globales du navigateur (ex: localStorage, fetch)
        // pour que ESLint ne dise pas qu'elles sont "non définies"
        ...globals.browser,
      },
    },

    // 6. DÉFINITION DES RÈGLES
    rules: {
      // Désactive l'obligation d'importer 'React' en haut de chaque fichier.
      // Indispensable pour React 17, 18 et 19 qui gèrent cela automatiquement.
      "react/react-in-jsx-scope": "off",

      // Signale les variables créées mais jamais utilisées (ex: un import oublié).
      // Mis en "warn" pour ne pas bloquer le build mais alerter le développeur.
      "no-unused-vars": "warn",

      // Force le linter à considérer que 'React' est utilisé s'il y a du JSX.
      // (Sécurité supplémentaire pour la compatibilité).
      "react/jsx-uses-react": "error",

      // Empêche ESLint de marquer tes composants (comme <Login /> ou <Stock />)
      // comme "inutilisés" s'ils ne sont présents que dans ton code JSX.
      "react/jsx-uses-vars": "error",
    },
  },
];
```

**Pour le CSS**

Dans le fichier src/frontend/src/ : `.stylelintrc.json`

**Attention** json n'accepte pas les commentaires

```
{
  // 1. EXTENSION DU PACK DE RÈGLES STANDARDS
  // On ne repart pas de zéro : on importe les meilleures pratiques de la communauté CSS.
  // Cela vérifie par défaut les erreurs de frappe, les unités invalides (ex: 10pxx), etc.
  "extends": ["stylelint-config-standard"],

  "rules": {
    // 2. GESTION DES LIGNES VIDES DANS LES COMMENTAIRES
    // Par défaut, Stylelint force une ligne vide avant chaque commentaire.
    // En mettant "null", on autorise d'écrire un commentaire juste après une ligne de code
    // sans être bloqué par une erreur.
    "comment-empty-line-before": null,

    // 3. PRIORITÉ DES SÉLECTEURS (Spécificité)
    // Normalement, Stylelint interdit d'écrire un sélecteur moins spécifique après un plus spécifique
    // (ex: écrire 'h1' après '.ma-classe h1').
    // On le désactive ici pour vous laisser plus de liberté dans l'organisation de vos fichiers.
    "no-descending-specificity": null,

    // 4. PROTECTION CONTRE LES MOTS-CLÉS INCONNUS
    // Cette règle empêche d'utiliser des commandes CSS qui n'existent pas (ex: @erreur).
    // Cependant, on ajoute une liste d'exceptions ("ignoreAtRules") pour que Stylelint
    // ne panique pas s'il croise des outils modernes comme Tailwind ou PostCSS.
    "at-rule-no-unknown": [
      true,
      {
        "ignoreAtRules": [
          "tailwind",   // Autorise @tailwind
          "apply",      // Autorise @apply (très courant pour factoriser le CSS)
          "variants",   // Autorise @variants
          "responsive", // Autorise @responsive
          "screen"      // Autorise @screen (pour les media queries personnalisées)
        ]
      }
    ]
  }
}
```

______________________________________________________________________

## 🧹 Maintenance : Nettoyage complet de l'existant

Si vous souhaitez formater et linter l'intégralité du projet (et non pas seulement vos modifications en cours), utilisez les commandes suivantes à la racine du dépôt projet2A :

### 🐍 Backend (Python)

Utilise Ruff pour traiter tous les fichiers .py en suivant les règles définies dans le `pyproject.toml.`

```bash
# Analyse et correction automatique des erreurs logiques et imports
ruff check --fix .

# Formatage du style (espaces, indentations, guillemets)
ruff format .
```

### ⚛️ Frontend (React & JS)

Utilise ESLint pour la logique React et Prettier pour le style visuel.

```bash
# Lintage avec la configuration spécifique située dans le src
npx eslint -c src/frontend/src/eslint.config.js --fix src/frontend/src/

# Formatage de tous les fichiers frontend
npx prettier --write "src/frontend/src/"
```

### 🎨 Styles (CSS)

Utilise Stylelint pour valider la syntaxe CSS.

```Bash
# Vérification de la validité du CSS (couleurs, propriétés, doublons)
npx stylelint --config src/frontend/src/.stylelintrc.json --fix "src/frontend/src/**/*.css"
```

### 📝 Documentation (Markdown)

```Bash
# Standardisation de tous les fichiers .md du projet
mdformat .
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

echo "=== Hook pre-commit : Vérification Qualité Code ==="

# =============================================
# Étape 1 - Identification des fichiers modifiés
# =============================================

# Python (fichiers .py)
STAGED_PY=$(git diff --cached --name-only --diff-filter=d | grep '\.py$' || true)

# Frontend JS/React (fichiers .js, .jsx, .ts, .tsx)
STAGED_FE=$(git diff --cached --name-only --diff-filter=d | grep -E '\.(js|jsx|ts|tsx)$' || true)

# Styles (fichiers .css)
STAGED_CSS=$(git diff --cached --name-only --diff-filter=d | grep '\.css$' || true)

# Documentation (fichiers .md)
STAGED_MD=$(git diff --cached --name-only --diff-filter=d | grep '\.md$' || true)

# =============================================
# Étape 2 - Routine Python (Ruff)
# =============================================
if [ -n "$STAGED_PY" ]; then
    echo "[PYTHON] Analyse et formatage (Ruff)..."
    # Utilise le pyproject.toml à la racine
    ruff check --fix $STAGED_PY
    ruff format $STAGED_PY
fi

# =============================================
# Étape 3 - Routine Frontend (ESLint + Prettier)
# =============================================
if [ -n "$STAGED_FE" ]; then
    echo "[JS/REACT] Lintage (ESLint)..."
    # Utilise ta config spécifique dans le src
    npx eslint -c src/frontend/src/eslint.config.js --fix $STAGED_FE

    echo "[JS/REACT] Formatage (Prettier)..."
    npx prettier --write $STAGED_FE
fi

# =============================================
# Étape 4 - Routine Styles (Stylelint)
# =============================================
if [ -n "$STAGED_CSS" ]; then
    echo "[CSS] Lintage (Stylelint)..."
    # Utilise ta config spécifique dans le src
    npx stylelint --config src/frontend/src/.stylelintrc.json --fix $STAGED_CSS

    echo "[CSS] Formatage (Prettier)..."
    npx prettier --write $STAGED_CSS
fi

# =============================================
# Étape 5 - Routine Markdown (mdformat)
# =============================================
if [ -n "$STAGED_MD" ]; then
    echo "[DOC] Formatage Markdown (mdformat)..."
    mdformat $STAGED_MD
fi

# =============================================
# Étape 6 - Mise à jour du staging
# =============================================
# On regroupe tous les fichiers pour les rajouter au commit après correction
ALL_STAGED="$STAGED_PY $STAGED_FE $STAGED_CSS $STAGED_MD"

# On nettoie les espaces pour vérifier s'il y a des fichiers à ajouter
CLEAN_STAGED=$(echo $ALL_STAGED | xargs)

if [ -n "$CLEAN_STAGED" ]; then
    git add $CLEAN_STAGED
    echo "---"
    echo "✅ Corrections automatiques appliquées et ajoutées au commit."
fi

echo "🚀 Toutes les vérifications sont passées. Commit autorisé."
exit 0
```

Rendre le hooks pre-commit executable

```bash
chmod +x .git/hooks/pre-commit
```
