from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import re
from typing import Any

import requests


SPOONACULAR_BASE_URL = "https://api.spoonacular.com"


# ============================================================
# Exceptions
# ============================================================


class SpoonacularError(RuntimeError):
    """Erreur générique liée à Spoonacular."""


class SpoonacularAuthError(SpoonacularError):
    """Clé API absente/invalide ou non autorisée."""


class SpoonacularRateLimitError(SpoonacularError):
    """Quota/rate limit dépassé."""


class SpoonacularBadRequestError(SpoonacularError):
    """Requête invalide (paramètres incorrects, etc.)."""


# ============================================================
# Helpers
# ============================================================


def _normalize_ingredient(s: str) -> str:
    """
    Normalise un ingrédient pour l'envoyer à l'API.
    - strip
    - minuscules
    - espaces multiples -> 1 espace
    - retire ponctuation "lourde" (garde lettres/nombres/espace/-/)
    """
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    # On retire la ponctuation trop agressive, sans casser "semi-dried" ou "1/2"
    s = re.sub(r"[^a-z0-9\s\-/]", "", s)
    return s.strip()


def _build_include_ingredients(ingredients: Sequence[str]) -> str:
    """
    Construit la valeur du paramètre includeIngredients:
    une liste d'ingrédients séparés par des virgules.
    """
    cleaned: list[str] = []
    seen: set[str] = set()

    for ing in ingredients:
        norm = _normalize_ingredient(ing)
        if not norm:
            continue
        if norm in seen:
            continue
        seen.add(norm)
        cleaned.append(norm)

    if not cleaned:
        raise ValueError("La liste d'ingrédients est vide après normalisation.")

    # Spoonacular attend une chaîne "tomato,cheese"
    return ",".join(cleaned)


def _raise_for_spoonacular_error(resp: requests.Response) -> None:
    """
    Transforme les erreurs HTTP Spoonacular en exceptions explicites.
    Spoonacular renvoie souvent un JSON avec un champ 'message'.
    """
    if 200 <= resp.status_code < 300:
        return

    msg = None
    try:
        data = resp.json()
        msg = data.get("message") or data.get("error") or str(data)
    except Exception:
        msg = resp.text or f"HTTP {resp.status_code}"

    if resp.status_code in (401, 403):
        raise SpoonacularAuthError(
            f"Spoonacular auth error ({resp.status_code}): {msg}"
        )
    if resp.status_code == 402:
        # Spoonacular utilise 402 pour "quota exceeded" sur certains plans
        raise SpoonacularRateLimitError(f"Spoonacular quota exceeded (402): {msg}")
    if resp.status_code == 429:
        raise SpoonacularRateLimitError(f"Spoonacular rate limit (429): {msg}")
    if resp.status_code == 400:
        raise SpoonacularBadRequestError(f"Spoonacular bad request (400): {msg}")

    raise SpoonacularError(f"Spoonacular error ({resp.status_code}): {msg}")


# ============================================================
# Résultats de recherche (complexSearch)
# ============================================================


@dataclass(frozen=True)
class RecipeSearchResult:
    id: int
    title: str
    image: str | None = None
    image_type: str | None = None
    # Optionnel si addRecipeInformation/fillIngredients etc.
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class RecipeSearchResponse:
    offset: int
    number: int
    total_results: int
    results: list[RecipeSearchResult]


def search_recipes_by_ingredients(
    api_key: str,
    ingredients: Sequence[str],
    n: int = 10,
    *,
    # filtres/paramètres de l'endpoint complexSearch
    cuisine: str | Sequence[str] | None = None,
    exclude_cuisine: str | Sequence[str] | None = None,
    diet: str | None = None,
    intolerances: str | Sequence[str] | None = None,
    type_: str | None = None,
    max_ready_time: int | None = None,
    min_servings: int | None = None,
    max_servings: int | None = None,
    ignore_pantry: bool = True,
    instructions_required: bool = True,
    fill_ingredients: bool = True,
    add_recipe_information: bool = False,
    add_recipe_instructions: bool = False,
    add_recipe_nutrition: bool = False,
    sort: str | None = "max-used-ingredients",
    sort_direction: str | None = None,  # "asc" ou "desc"
    offset: int = 0,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> RecipeSearchResponse:
    """
    Cherche des recettes Spoonacular à partir d'une liste d'ingrédients, via:
      GET /recipes/complexSearch?includeIngredients=...

    Paramètres clés
    --------------
    api_key : str
        Ta clé Spoonacular.
    ingredients : Sequence[str]
        Liste d'ingrédients ("tomato", "cheese", "chicken breast", ...).
    n : int
        Nombre de recettes désirées (1..100).
    sort :
        Très utile pour un mode "frigo":
        - "max-used-ingredients" : favorise les recettes qui utilisent le plus
          d'ingrédients fournis.
        - "min-missing-ingredients" : favorise celles qui en "manquent" le moins.

    Retours
    -------
    RecipeSearchResponse : structure typée avec results (id, title, image, ...)

    Exceptions
    ----------
    ValueError si inputs invalides
    SpoonacularAuthError / SpoonacularRateLimitError / SpoonacularBadRequestError /
    SpoonacularError
    """
    if not api_key or not isinstance(api_key, str):
        raise ValueError("api_key doit être une chaîne non vide.")

    if not isinstance(ingredients, (list, tuple)) or len(ingredients) == 0:
        raise ValueError("ingredients doit être une liste/tuple non vide.")

    if not (1 <= n <= 100):
        raise ValueError("n doit être compris entre 1 et 100 (limite de l'API).")

    if offset < 0 or offset > 900:
        # doc: offset 0..900
        raise ValueError("offset doit être entre 0 et 900.")

    include_ingredients = _build_include_ingredients(ingredients)

    def _csv(v: str | Sequence[str]) -> str:
        if isinstance(v, str):
            return v
        return ",".join(str(x) for x in v)

    params: dict[str, Any] = {
        "apiKey": api_key,
        "includeIngredients": include_ingredients,
        "number": n,
        "offset": offset,
        "ignorePantry": str(ignore_pantry).lower(),  # "true"/"false"
        "instructionsRequired": str(instructions_required).lower(),
    }

    # Options utiles
    if cuisine:
        params["cuisine"] = _csv(cuisine)
    if exclude_cuisine:
        params["excludeCuisine"] = _csv(exclude_cuisine)
    if diet:
        params["diet"] = diet
    if intolerances:
        params["intolerances"] = _csv(intolerances)
    if type_:
        params["type"] = type_
    if max_ready_time is not None:
        if max_ready_time <= 0:
            raise ValueError("max_ready_time doit être > 0.")
        params["maxReadyTime"] = max_ready_time
    if min_servings is not None:
        if min_servings <= 0:
            raise ValueError("min_servings doit être > 0.")
        params["minServings"] = min_servings
    if max_servings is not None:
        if max_servings <= 0:
            raise ValueError("max_servings doit être > 0.")
        params["maxServings"] = max_servings

    # Informations additionnelles (attention quotas)
    params["fillIngredients"] = str(fill_ingredients).lower()
    params["addRecipeInformation"] = str(add_recipe_information).lower()
    params["addRecipeInstructions"] = str(add_recipe_instructions).lower()
    params["addRecipeNutrition"] = str(add_recipe_nutrition).lower()

    if sort:
        params["sort"] = sort
    if sort_direction:
        if sort_direction not in ("asc", "desc"):
            raise ValueError("sort_direction doit être 'asc' ou 'desc'.")
        params["sortDirection"] = sort_direction

    url = f"{SPOONACULAR_BASE_URL}/recipes/complexSearch"

    sess = session or requests.Session()
    try:
        resp = sess.get(url, params=params, timeout=timeout)
    except requests.Timeout as e:
        raise SpoonacularError(f"Timeout en appelant Spoonacular: {e}") from e
    except requests.RequestException as e:
        raise SpoonacularError(f"Erreur réseau en appelant Spoonacular: {e}") from e

    _raise_for_spoonacular_error(resp)

    data = resp.json()

    # Parsing robuste
    offset_val = int(data.get("offset", 0))
    number_val = int(data.get("number", 0))
    total = int(data.get("totalResults", 0))  # clé JSON Spoonacular
    raw_results = data.get("results", []) or []

    results: list[RecipeSearchResult] = []
    for r in raw_results:
        rid = int(r.get("id"))
        title = str(r.get("title", "")).strip()

        image = r.get("image")
        image_type = r.get("imageType")  # clé JSON Spoonacular

        extra = dict(r)
        for k in ("id", "title", "image", "imageType"):
            extra.pop(k, None)

        results.append(
            RecipeSearchResult(
                id=rid,
                title=title,
                image=image,
                image_type=image_type,
                extra=extra or None,
            )
        )

    return RecipeSearchResponse(
        offset=offset_val,
        number=number_val,
        total_results=total,
        results=results,
    )


# ============================================================
# Recettes détaillées (informationBulk)
# ============================================================


@dataclass(frozen=True)
class DetailedIngredient:
    name: str
    amount: float
    unit: str
    original: str


@dataclass(frozen=True)
class DetailedStep:
    number: int
    step: str


@dataclass(frozen=True)
class DetailedRecipe:
    id: int
    title: str
    image: str | None
    ready_in_minutes: int | None
    servings: int | None
    ingredients: list[DetailedIngredient]
    steps: list[DetailedStep]
    source_url: str | None = None


def fetch_detailed_recipes_by_ingredients(
    api_key: str,
    ingredients: Sequence[str],
    n: int = 5,
    *,
    sort: str = "max-used-ingredients",
    ignore_pantry: bool = True,
    instructions_required: bool = True,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[DetailedRecipe]:
    """
    Outil haut niveau :
    - Recherche des recettes par ingrédients (complexSearch)
    - Récupère les ingrédients (quantités/unités) + étapes (informationBulk)
    """
    search = search_recipes_by_ingredients(
        api_key=api_key,
        ingredients=ingredients,
        n=n,
        sort=sort,
        ignore_pantry=ignore_pantry,
        instructions_required=instructions_required,
        # IMPORTANT: on garde la recherche "légère" (moins de quota)
        fill_ingredients=False,
        add_recipe_information=False,
        add_recipe_instructions=False,
        add_recipe_nutrition=False,
        timeout=timeout,
        session=session,
    )

    ids = [r.id for r in search.results]
    if not ids:
        return []

    url = f"{SPOONACULAR_BASE_URL}/recipes/informationBulk"
    params: dict[str, Any] = {
        "apiKey": api_key,
        "ids": ",".join(map(str, ids)),
        "addRecipeInformation": "true",
        "addRecipeInstructions": "true",
    }

    sess = session or requests.Session()
    try:
        resp = sess.get(url, params=params, timeout=timeout)
    except requests.Timeout as e:
        raise SpoonacularError(f"Timeout en appelant Spoonacular: {e}") from e
    except requests.RequestException as e:
        raise SpoonacularError(f"Erreur réseau en appelant Spoonacular: {e}") from e

    _raise_for_spoonacular_error(resp)

    recipes_info = resp.json()
    if not isinstance(recipes_info, list):
        raise SpoonacularError(
            "Réponse inattendue de informationBulk (liste attendue)."
        )

    detailed: list[DetailedRecipe] = []
    for info in recipes_info:
        ingredients_out: list[DetailedIngredient] = []
        for ing in info.get("extendedIngredients", []) or []:
            name = str(ing.get("name", "")).strip()
            if not name:
                continue

            try:
                amount = float(ing.get("amount", 0.0))
            except Exception:
                amount = 0.0

            ingredients_out.append(
                DetailedIngredient(
                    name=name,
                    amount=amount,
                    unit=str(ing.get("unit", "")).strip(),
                    original=str(ing.get("original", "")).strip(),
                )
            )

        steps_out: list[DetailedStep] = []
        for section in info.get("analyzedInstructions", []) or []:
            for st in section.get("steps", []) or []:
                text = str(st.get("step", "")).strip()
                if not text:
                    continue
                steps_out.append(
                    DetailedStep(
                        number=int(st.get("number", len(steps_out) + 1)),
                        step=text,
                    )
                )

        detailed.append(
            DetailedRecipe(
                id=int(info["id"]),
                title=str(info.get("title", "")).strip(),
                image=info.get("image"),
                ready_in_minutes=info.get("readyInMinutes"),
                servings=info.get("servings"),
                ingredients=ingredients_out,
                steps=steps_out,
                source_url=info.get("sourceUrl"),
            )
        )

    return detailed
