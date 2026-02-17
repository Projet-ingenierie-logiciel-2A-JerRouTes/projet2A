import os

from deep_translator import GoogleTranslator
from dotenv import load_dotenv

from clients.spoonacular_client import fetch_detailed_recipes_by_ingredients


def _translate(text: str, *, target: str = "fr") -> str:
    """
    Traduit un texte via GoogleTranslator (deep-translator).
    Gère les textes vides et évite de faire planter le script si la traduction échoue.
    """
    text = (text or "").strip()
    if not text:
        return ""

    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        # Fallback: on renvoie le texte original si la traduction échoue
        return text


def print_detailed_recipes(recipes, *, translate: bool = True):
    print("Mise en page propre : ")

    for r in recipes:
        # --- Titre + (optionnel) titre traduit
        title_fr = _translate(r.title) if translate else ""

        print("\n" + "=" * 70)
        print(f"{r.title}  (id={r.id})")
        if translate and title_fr and title_fr.lower() != r.title.lower():
            print(f"➡️  {title_fr}  [FR]")

        # --- Meta
        if r.ready_in_minutes is not None:
            print(f"⏱ {r.ready_in_minutes} min", end="")
            if r.servings is not None:
                print(f"  |  🍽 {r.servings} portions")
            else:
                print()
        if r.source_url:
            print(f"🔗 {r.source_url}")

        # --- Ingrédients (avec traduction optionnelle)
        print("\nIngrédients :")
        for ing in r.ingredients:
            qty = f"{ing.amount:g}"
            unit = f" {ing.unit}" if ing.unit else ""

            ing_name_fr = _translate(ing.name) if translate else ""
            if translate and ing_name_fr and ing_name_fr.lower() != ing.name.lower():
                print(f" - {qty}{unit} {ing.name}  →  {ing_name_fr}")
            else:
                print(f" - {qty}{unit} {ing.name}")

        # --- Étapes (avec traduction optionnelle)
        print("\nPréparation :")
        if not r.steps:
            print(" - (Pas d'instructions structurées fournies)")
        else:
            for st in sorted(r.steps, key=lambda s: s.number):
                step_fr = _translate(st.step) if translate else ""
                print(f" {st.number}. {st.step}")
                if translate and step_fr and step_fr.lower() != st.step.lower():
                    print(f"    ↳ {step_fr}")


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("API_KEY_SPOONACULAR")
    if not api_key:
        raise RuntimeError("API_KEY_SPOONACULAR manquante dans le .env")

    ingredients = ["tomato", "mozzarella", "basil", "olive oil"]

    # recipes = fetch_detailed_recipes_by_ingredients(
    #     api_key=api_key,
    #     ingredients=ingredients,
    #     n=3,
    #     sort="max-used-ingredients",
    #     ignore_pantry=True,
    #     instructions_required=True,
    # )

    # recipes = fetch_detailed_recipes_by_ingredients(
    #     api_key=api_key,
    #     ingredients=[
    #         "tomato",
    #         "salt",
    #         "olive oil",
    #         "sugar",
    #         "butter",
    #         "flour",
    #         "chocolate",
    #     ],
    #     dish_type="dessert",
    #     sort ="min-missing-ingredients",
    #     n=5,
    # )

    ## ça ne marche pas encore comme recherche
    recipes = fetch_detailed_recipes_by_ingredients(
        api_key=api_key,
        ingredients=["flour", "sugar", "butter", "eggs", "milk"],
        n=10,
        dish_type="dessert",
        strict_only=True,
        max_missing_ingredients=0,
    )

    # translate=True pour afficher la version FR
    print_detailed_recipes(recipes, translate=True)
