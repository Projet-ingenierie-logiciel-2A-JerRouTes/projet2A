from pathlib import Path

import pandas as pd


ODS_PATH = Path("data/ingrédients.ods")
OUT_CSV = Path("data/ingredients.csv")


def main():
    xls = pd.ExcelFile(ODS_PATH, engine="odf")

    all_rows = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(ODS_PATH, engine="odf", sheet_name=sheet, header=None)

        # 1 seule colonne attendue : le nom de l'ingrédient
        col = df.columns[0]
        names = df[col].dropna().astype(str).str.strip()
        names = names[names != ""]

        for name in names:
            all_rows.append({"nom": name, "categorie": sheet})

    out = pd.DataFrame(all_rows).drop_duplicates()
    out.to_csv(OUT_CSV, index=False, encoding="utf-8")

    print(f"OK -> {OUT_CSV} ({len(out)} lignes)")

    def _load_ingredients_from_ods(_self, cursor, ods_path="data/ingrédients.ods"):
        ods_path = Path(ods_path)
        if not ods_path.exists():
            print(f"[WARN] Fichier introuvable: {ods_path} (ingrédients non chargés)")
            return

        xls = pd.ExcelFile(ods_path, engine="odf")

        seen = set()
        rows = []

        for sheet in xls.sheet_names:
            df = pd.read_excel(ods_path, engine="odf", sheet_name=sheet, header=None)
            if df.empty:
                continue

            first_col = df.columns[0]
            names = df[first_col].dropna().astype(str).str.strip()
            names = names[names != ""]

            for name in names:
                key = name.casefold()  # robuste pour accents/casse
                if key not in seen:
                    seen.add(key)
                    rows.append((name,))

        if not rows:
            print("[WARN] Aucun ingrédient trouvé dans l'ODS")
            return

        cursor.executemany(
            """
            INSERT INTO ingredient (name, unit)
            VALUES (%s, NULL)
            ON CONFLICT ((LOWER(name))) DO NOTHING;
            """,
            rows,
        )

        print(f"[OK] {len(rows)} ingrédients chargés depuis {ods_path}")


if __name__ == "__main__":
    main()
