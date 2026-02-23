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


if __name__ == "__main__":
    main()
