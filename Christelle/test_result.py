import requests


# L'URL de votre propre API FastAPI (locale)
URL_LOCALE = "http://127.0.0.1:8000/recettes"


def chercher_recettes(ingredients):
    """Envoie une requête à notre serveur FastAPI"""
    params = {"ingredients": ingredients}

    try:
        response = requests.get(URL_LOCALE, params=params)
        # Vérifie si la requête a réussi (code 200)
        response.raise_for_status()

        recettes = response.json()

        print(f"--- {len(recettes)} recettes trouvées avec : {ingredients} ---")
        for r in recettes:
            print(f"- {r['title']} (ID: {r['id']})")

    except requests.exceptions.ConnectionError:
        print(
            "Erreur : Assurez-vous que votre serveur FastAPI est bien lancé sur le port 8000 !"
        )
    except Exception as e:
        print(f"Une erreur est survenue : {e}")


if __name__ == "__main__":
    # Test avec l'ingrédient oeuf (egg)
    chercher_recettes("egg")
