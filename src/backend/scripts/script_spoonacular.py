import os

from dotenv import load_dotenv

from src.backend.clients.spoonacular_client import fetch_detailed_recipes_by_ingredients


def print_detailed_recipes(recipes):
    for r in recipes:
        print("\n" + "=" * 70)
        print(f"{r.title} (id={r.id})")

        print("\nIngrédients :")
        for ing in r.ingredients:
            qty = f"{ing.amount:g}"
            unit = f" {ing.unit}" if ing.unit else ""
            print(f" - {qty}{unit} {ing.name}")

        print("\nPréparation :")
        if not r.steps:
            print(" - (Pas d'instructions structurées)")
        else:
            for st in sorted(r.steps, key=lambda s: s.number):
                print(f" {st.number}. {st.step}")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("API_KEY_SPOONACULAR")
    if not api_key:
        raise RuntimeError("API_KEY_SPOONACULAR manquante dans le .env")

    recipes = fetch_detailed_recipes_by_ingredients(
        api_key=api_key,
        ingredients=["tomato", "mozzarella", "basil", "olive oil"],
        n=3,
    )

    print_detailed_recipes(recipes)
