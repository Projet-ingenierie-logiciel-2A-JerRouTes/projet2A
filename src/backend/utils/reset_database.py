import logging
import os
from pathlib import Path
import sys
from unittest import mock

import dotenv


# Ajout automatique de src/ au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dao.db_connection import DBConnection
from utils.ingredients_loader import load_ingredients
from utils.ingredients_tags_loader import load_ingredients_tags
from utils.log_decorator import log
from utils.singleton import Singleton


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INIT_SQL_PATH = DATA_DIR / "init_db.sql"
POP_TEST_SQL_PATH = DATA_DIR / "pop_db_test.sql"
POP_SQL_PATH = DATA_DIR / "pop_db.sql"


def _strip_sql_comments(sql: str) -> str:
    """
    Retire les commentaires SQL pour détecter si un fichier contient
    du SQL réellement exécutable (et pas juste des lignes '-- ...').

    - enlève les lignes '-- ...'
    - enlève les blocs '/* ... */'
    """
    # Enlever blocs /* ... */
    out = []
    i = 0
    n = len(sql)
    while i < n:
        if i + 1 < n and sql[i] == "/" and sql[i + 1] == "*":
            # skip until */
            i += 2
            while i + 1 < n and not (sql[i] == "*" and sql[i + 1] == "/"):
                i += 1
            i += 2  # skip */
            continue
        out.append(sql[i])
        i += 1
    no_block = "".join(out)

    # Enlever commentaires -- ...
    lines = []
    for line in no_block.splitlines():
        # on coupe au premier '--'
        if "--" in line:
            line = line.split("--", 1)[0]
        lines.append(line)
    return "\n".join(lines).strip()


def _has_executable_sql(sql: str | None) -> bool:
    if not sql:
        return False
    return bool(_strip_sql_comments(sql))


class ResetDatabase(metaclass=Singleton):
    @log
    def lancer(self, test_dao=True, populate=True):
        """
        Réinitialisation de la base

        - test_dao=True  -> schéma projet_test_dao
        - populate=True  -> insère les données SQL (si fichier contient du SQL exécutable)
        """
        dotenv.load_dotenv()

        if test_dao:
            schema = "projet_test_dao"
            pop_data_path = POP_TEST_SQL_PATH
        else:
            schema = "projet_dao"
            pop_data_path = POP_SQL_PATH

        with mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": schema}):
            self._reset_schema(schema, pop_data_path if populate else None)

    def _reset_schema(self, schema, pop_data_path):
        print(f"\n🔄 Initialisation du schéma : {schema}")

        create_schema_sql = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        )

        if not INIT_SQL_PATH.exists():
            raise FileNotFoundError(f"Fichier manquant : {INIT_SQL_PATH}")

        with INIT_SQL_PATH.open(encoding="utf-8") as f:
            init_db_sql = f.read()

        if not _has_executable_sql(init_db_sql):
            raise ValueError(
                f"Le fichier ne contient aucun SQL exécutable : {INIT_SQL_PATH}"
            )

        pop_db_sql = None
        if pop_data_path and pop_data_path.exists():
            with pop_data_path.open(encoding="utf-8") as f:
                pop_db_sql = f.read()

        run_pop = _has_executable_sql(pop_db_sql)

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Drop + Create schema
                    cursor.execute(create_schema_sql)

                    # Set search path
                    cursor.execute(f"SET search_path TO {schema};")

                    # Création structure
                    cursor.execute(init_db_sql)

                    # Insertion données SQL seulement si il y a du SQL exécutable
                    if pop_data_path and pop_db_sql is not None and not run_pop:
                        print(
                            f"ℹ️ {pop_data_path} ne contient que des commentaires : aucune donnée SQL insérée."
                        )
                    if run_pop:
                        cursor.execute(pop_db_sql)

                    # Import CSV ingrédients
                    load_ingredients(cursor)

                    # Import ODS ingrédients + tags
                    load_ingredients_tags(cursor)

                connection.commit()

            if run_pop:
                print(f"✅ Schéma {schema} réinitialisé avec données.\n")
            else:
                print(f"✅ Schéma {schema} réinitialisé (structure seule).\n")

        except Exception:
            logging.exception(
                f"❌ Erreur lors de la réinitialisation du schéma {schema}"
            )
            raise


if __name__ == "__main__":
    dotenv.load_dotenv()

    resetter = ResetDatabase()

    # À toi de choisir ce que tu veux lancer en direct:
    # resetter.lancer(test_dao=True, populate=True)
    resetter.lancer(test_dao=False, populate=True)
