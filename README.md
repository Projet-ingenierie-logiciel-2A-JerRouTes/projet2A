# Projet 2A

## Analyse statique et qualité du code

Ce projet met en place des outils d’analyse statique afin d’améliorer la qualité,
la cohérence et la maintenabilité du code Python.

Les règles de linting et de formatting sont définies de manière centralisée
et peuvent être appliquées automatiquement sur l’ensemble du projet.

### Outils

- **Ruff**  
  Utilisé comme linter et formatter pour Python.

### Installation dans projet

```bash
uv init
uv sync
uv add --dev ruff
```

### Utilisation

#### Analyse statique (linting)

Analyser le code et afficher les problèmes détectés :

```bash
uv run ruff check
```

Corriger automatiquement les problèmes simples :

```bash
uv run ruff check --fix
```

#### Formatage du code

Vérifier que le code respecte les règles de formatage :

```bash
uv run ruff format --check
```

Appliquer le formatage automatique :

```bash
uv run ruff format
```

### Configuration

La configuration de Ruff est définie dans le fichier `ruff.toml` à la racine du projet.