from collections.abc import Iterable
import csv
from pathlib import Path


def _candidate_csv_paths() -> Iterable[Path]:
    backend_dir = Path(__file__).resolve().parents[1]
    repo_dir = backend_dir.parents[2]

    # Priorité future : data côté backend
    yield backend_dir / "data" / "ingredients.csv"

    # Emplacement actuel (racine projet)
    yield repo_dir / "data" / "ingredients.csv"


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

        # Ton fichier: nom,categorie (ou name,categorie)
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
