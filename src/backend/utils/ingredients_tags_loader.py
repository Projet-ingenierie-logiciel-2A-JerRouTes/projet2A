from pathlib import Path
import pandas as pd


def load_ingredients_tags(cursor):
    """
    Charge les ingrédients et leurs tags depuis un fichier ODS.

    - Chaque feuille du fichier représente un tag.
    - Chaque ligne d'une feuille représente un ingrédient.
    - La fonction est idempotente :
        -> ne recrée pas les tags existants
        -> ne recrée pas les ingrédients existants
        -> ne recrée pas les relations existantes
    - Le commit est géré par le code appelant (ResetDatabase).
    """

    # Récupération du chemin absolu vers le dossier backend/
    base_dir = Path(__file__).resolve().parent.parent

    # Chemin vers le fichier ODS contenant les données
    file_path = base_dir / "data" / "ingredients.ods"

    # Si le fichier n'existe pas, on arrête proprement l'import
    if not file_path.exists():
        print("Fichier ingredients.ods non trouvé. Import ignoré.")
        return

    print("Import des ingrédients + tags depuis le fichier ODS...")

    # Ouverture du fichier ODS avec pandas (nécessite odfpy)
    excel = pd.ExcelFile(file_path, engine="odf")

    # Parcours de chaque feuille (chaque feuille = 1 tag)
    for sheet_name in excel.sheet_names:

        # Nettoyage du nom de la feuille
        tag_name = sheet_name.strip()

        # Insertion du tag (si non existant)
        cursor.execute(
            """
            INSERT INTO tag(name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING;
            """,
            (tag_name,),
        )

        # Lecture de la feuille sans header (toutes les lignes = ingrédients)
        df = excel.parse(sheet_name, header=None)

        # Parcours de la première colonne uniquement
        for ingredient_name in df.iloc[:, 0].dropna():

            # Nettoyage du texte
            ingredient_name = str(ingredient_name).strip()

            # Ignore les lignes vides
            if not ingredient_name:
                continue

            # Insertion de l’ingrédient (si non existant)
            cursor.execute(
                """
                INSERT INTO ingredient(name)
                VALUES (%s)
                ON CONFLICT DO NOTHING;
                """,
                (ingredient_name,),
            )

            # Création de la relation ingrédient ↔ tag
            cursor.execute(
                """
                INSERT INTO ingredient_tag(fk_ingredient_id, fk_tag_id)
                SELECT i.ingredient_id, t.tag_id
                FROM ingredient i
                JOIN tag t ON t.name = %s
                WHERE LOWER(i.name) = LOWER(%s)
                ON CONFLICT DO NOTHING;
                """,
                (tag_name, ingredient_name),
            )

    print("Import ingrédients + tags terminé avec succès")
