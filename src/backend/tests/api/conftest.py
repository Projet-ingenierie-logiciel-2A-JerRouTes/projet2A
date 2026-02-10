import os

from fastapi.testclient import TestClient
import pytest

# ⚠️ adapte l'import de ton app FastAPI si besoin
from src.backend.api.main import app
from src.backend.utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def _force_test_schema_and_reset_db():
    """
    - Force le schéma de test pour toute la session de tests
    - Réinitialise le schéma test une fois au début
    - Important avec le Singleton: on "reset" la connexion pour éviter
      qu'elle garde un ancien search_path.
    """
    os.environ["POSTGRES_SCHEMA"] = "projet_test_dao"

    # Reset DB test (drop/create + init + populate test)
    ResetDatabase().lancer(test_dao=True)

    # Si DBConnection a déjà été instanciée ailleurs, on veut éviter
    # qu'elle garde l'ancienne connexion/schema.
    # Selon ton Singleton, tu peux avoir besoin d'une méthode de reset.
    # Si tu n'en as pas, le plus simple est d'éviter d'instancier DBConnection avant.
    yield


@pytest.fixture()
def client():
    return TestClient(app)
