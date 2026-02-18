from __future__ import annotations

from dataclasses import dataclass

from business_objects.recipe import Recipe
from services.find_recipe import FindRecipe, IngredientSearchQuery


"""Factory / façade unifiée de recherche de recettes.

Cette classe implémente l’interface `FindRecipe` et orchestre deux sources
de données :

- une source locale (BDD), considérée comme cache et source de vérité interne ;
- une source externe (API), utilisée en complément si nécessaire.

Architecture
------------
Le reste de l’application dépend uniquement de l’abstraction `FindRecipe`.
Cette factory encapsule la logique de fallback afin d’éviter que les couches
supérieures ne connaissent les détails d’implémentation (DB vs API).

Stratégie de résolution
------------------------
1. `get_by_id(recipe_id)`
   - L’identifiant `recipe_id` est un identifiant **interne BDD**.
   - Aucun fallback API n’est effectué (IDs API ≠ IDs internes).
   - La méthode délègue uniquement à la couche DB.

2. `search_by_ingredients(query)`
   - On interroge d’abord la BDD.
   - Si le nombre de résultats est insuffisant par rapport à `query.limit`,
     on complète via l’API.
   - Les résultats sont fusionnés et dédupliqués.
   - Selon la configuration de `api`, les recettes externes peuvent être
     persistées en BDD (logique de cache applicatif).

Contexte :
--------------------------
Dans ce projet, les identifiants internes BDD sont distincts des identifiants
externes fournis par l’API. Il serait donc incohérent de tenter un fallback
API à partir d’un `recipe_id` interne.
"""


@dataclass(slots=True)
class FindRecipeFactory(FindRecipe):
    """Implémentation composite de `FindRecipe` (DB + API).

    Attributs
    ---------
    db : FindRecipe
        Implémentation basée sur la base de données (cache interne).
    api : FindRecipe
        Implémentation basée sur l’API externe (source complémentaire).
    """

    db: FindRecipe
    api: FindRecipe

    def get_by_id(self, recipe_id: int) -> Recipe | None:
        """Retourne une recette par identifiant interne BDD.

        Aucun fallback API n’est effectué car `recipe_id`
        correspond exclusivement à une clé primaire interne.
        """
        return self.db.get_by_id(recipe_id)

    def search_by_ingredients(self, query: IngredientSearchQuery) -> list[Recipe]:
        """Recherche des recettes par ingrédients avec fallback API.

        La BDD est interrogée en priorité. Si le nombre de résultats
        est inférieur à la limite demandée, l’API est utilisée pour
        compléter les résultats.

        Les résultats DB et API sont fusionnés puis dédupliqués
        sur la base de l’identifiant de recette.
        """
        from_db = self.db.search_by_ingredients(query)
        if len(from_db) >= query.limit:
            return from_db[: query.limit]

        remaining = max(0, int(query.limit) - len(from_db))
        if remaining == 0:
            return from_db

        api_query = IngredientSearchQuery(
            ingredients=query.ingredients,
            limit=remaining,
            max_missing=query.max_missing,
            strict_only=query.strict_only,
            dish_type=query.dish_type,
            ignore_pantry=query.ignore_pantry,
        )
        from_api = self.api.search_by_ingredients(api_query)

        seen: set[int] = set()
        merged: list[Recipe] = []

        for r in [*from_db, *from_api]:
            rid = int(getattr(r, "recipe_id", 0) or 0)
            if rid and rid in seen:
                continue
            if rid:
                seen.add(rid)
            merged.append(r)
            if len(merged) >= query.limit:
                break

        return merged
