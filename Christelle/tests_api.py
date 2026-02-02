import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import httpx


load_dotenv()

app = FastAPI()

# Remplacez par votre véritable clé API Spoonacular
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes/findByIngredients"


@app.get("/recettes")
async def get_recipes(ingredients: str):
    """
    Recherche des recettes basées sur une liste d'ingrédients (ex: pommes,farine)
    """
    params = {"ingredients": ingredients, "number": 5, "apiKey": API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail="Erreur API Spoonacular"
            )

        return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
