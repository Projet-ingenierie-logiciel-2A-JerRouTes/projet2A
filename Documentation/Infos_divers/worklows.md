# Guide : Automatisation des tests unitaires avec GitHub Actions

Ce document explique les différentes étapes pour configurer le workflow GitHub Actions du projet, afin de lancer automatiquement les tests unitaires lorsque les fichiers user.py ou stock.py sont modifiés.

## Création du workflow GitHub Actions

Créer le fichier .github/workflows/tests.yml dans le dépôt :

```bash
name: Execution des tests si changement

on:
  push:
    paths:
      - 'src/business_objects/**'
  pull_request:
    paths:
      - 'src/business_objects/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.13

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
          pip install -e .

      - name: Run targeted tests
        run: |
          echo "=== Détection des fichiers modifiés ==="
          # Liste des fichiers modifiés dans business_objects/
          FILES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }} | grep '^src/business_objects/' || true)

          if [ -z "$FILES" ]; then
            echo "Aucun fichier modifié dans business_objects/, tests ignorés."
            exit 0
          fi

          echo "Fichiers modifiés :"
          echo "$FILES"
          echo

          # Pour chaque fichier modifié, déduire le test associé
          for f in $FILES; do
            # Récupérer le nom de base (ex: user.py → user)
            BASENAME=$(basename "$f" .py)
            TEST_FILE="tests/test_${BASENAME}.py"

            if [ -f "$TEST_FILE" ]; then
              echo "$f modifié → lancement $TEST_FILE"
              pytest "$TEST_FILE" -v
            else
              echo "Aucun test trouvé pour $f (attendu : $TEST_FILE)"
            fi
          done
```

## Fonctionnement :

1. Détection des fichiers modifiés :

- Tout fichier dans src/business_objects/ est récupéré automatiquement.

2. Mapping automatique :

- basename récupère le nom du fichier sans extension
- Construit le chemin du test correspondant (test\_<nom>.py) dans tests/

3. Exécution conditionnelle :

- Si le test existe → pytest est lancé
- Sinon → message d’avertissement

[⬅ Retour au README](../../README.md)
