import os
import sys


# Ajoute autohttps://github.com/Projet-ingenierie-logiciel-2A-JerRouTes/projet2Amatiquement le dossier parent (src/) au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import logging
from unittest import mock

import dotenv

from dao.db_connection import DBConnection
from utils.log_decorator import log
from utils.singleton import Singleton


class ResetDatabase(metaclass=Singleton):
    @log
    def lancer(self, test_dao=False, populate=True):
        """Lancement de la réinitialisation des données
        - test_dao=True  -> schéma de test
        - populate=False -> base vierge (structure uniquement)
        """

        dotenv.load_dotenv()

        if test_dao:
            schema = "projet_test_dao"
            pop_data_path = "data/pop_db_test.sql"
        else:
            schema = "projet_dao"
            pop_data_path = "data/pop_db.sql"

        with mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": schema}):
            self._reset_schema(schema, pop_data_path if populate else None)

    def _reset_schema(self, schema, pop_data_path):
        print(f" Initialisation du schéma : {schema}")

        create_schema = (
            f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        )

        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()

        pop_db_as_string = None
        if pop_data_path is not None:
            with open(pop_data_path, encoding="utf-8") as f:
                pop_db_as_string = f.read()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(create_schema)
                    cursor.execute(f"SET search_path TO {schema};")

                    cursor.execute(init_db_as_string)

                    # Charger les données seulement si demandé
                    if pop_db_as_string:
                        cursor.execute(pop_db_as_string)

                connection.commit()

            if pop_db_as_string:
                print(f"Schéma {schema} réinitialisé avec succès (avec données) !\n")
            else:
                print(f"Schéma {schema} réinitialisé avec succès (vierge) !\n")
        except Exception:
            logging.exception(
                f"Erreur lors de la réinitialisation du schéma {schema} :"
            )
            raise


if __name__ == "__main__":
    resetter = ResetDatabase()
    resetter.lancer(False, populate=False)  # projet_dao (vierge)
    resetter.lancer(True, populate=True)  # projet_test_dao (avec data)
