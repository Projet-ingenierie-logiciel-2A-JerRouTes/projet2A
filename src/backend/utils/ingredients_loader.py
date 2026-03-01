from collections.abc import Iterable
import csv
import os
from pathlib import Path


def _candidate_csv_paths() -> Iterable[Path]:
    here = Path(__file__).resolve()

    # (Optionnel mais super pratique) Permet de forcer le chemin via env var
    env_path = os.getenv("INGREDIENTS_CSV_PATH")
    if env_path:
        yield Path(env_path)

    # Dossier "backend" supposé (si utils/ est dans backend/)
    backend_dir = here.parents[1]  # ex: .../backend ou /app

    # Priorité : data côté backend
    yield backend_dir / "data" / "ingredients.csv"

    # Cas Docker de ton compose : tu montes ./src sur /app/src
    yield backend_dir / "src" / "backend" / "data" / "ingredients.csv"

    # Cas "repo racine/data" si tu as data/ à la racine du projet
    # On remonte tous les parents sans jamais indexer parents[2]
    for parent in backend_dir.parents:
        yield parent / "data" / "ingredients.csv"


def find_ingredients_csv_path() -> Path | None:
    for p in _candidate_csv_paths():
        if p.exists():
            return p
    return None


def load_ingredients_from_csv(cursor, csv_path: Path | None = None) -> int:
    if csv_path is None:
        csv_path = find_ingredients_csv_path()

    if csv_path is None:
        print("[WARN] Aucun fichier CSV d'ingrédients trouvé.")
        return 0

    seen: set[str] = set()
    rows: list[tuple[str]] = []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")

        for r in reader:
            name = (r.get("nom") or r.get("name") or "").strip()
            if not name:
                continue

            key = name.casefold()
            if key in seen:
                continue

            seen.add(key)
            rows.append((name,))

    if not rows:
        print(f"[WARN] CSV présent mais vide: {csv_path}")
        return 0

    cursor.executemany(
        """
        INSERT INTO ingredient (name, unit)
        VALUES (%s, NULL)
        ON CONFLICT ((LOWER(name))) DO NOTHING;
        """,
        rows,
    )

    print(f"[OK] Ingrédients importés depuis {csv_path} : {len(rows)}")
    return len(rows)


def load_ingredients(cursor) -> int:
    return load_ingredients_from_csv(cursor)
