from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from src.backend.business_objects.recipe import Recipe
from src.backend.business_objects.user import GenericUser
from src.backend.dao.db_connection import DBConnection
from src.backend.utils.log_decorator import log


@dataclass(frozen=True, slots=True)
class RecipeRow:
    """Représentation typée d'une ligne de la table `recipe`."""

    recipe_id: int
    fk_user_id: int | None
    name: str
    status: str | None
    prep_time: int | None
    portion: int | None
    description: str | None
    created_at: Any


class RecipeDAO:
    """DAO pour `recipe` + tables de liaison associées.

    Tables concernées :
    - recipe
    - recipe_ingredient
    - recipe_tag
    """

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def _row_to_bo(
        row: RecipeRow,
        *,
        ingredients: list[tuple[int, float]] | None = None,
        tags: list[tuple[int, str]] | None = None,
    ) -> Recipe:
        """Transforme une ligne BDD (+ relations) en objet métier `Recipe`."""

        user_id = int(row.fk_user_id or 0)

        creator = GenericUser(
            id_user=user_id,
            pseudo=f"user{user_id}" if user_id != 0 else "system",
            password="____",
        )

        recipe = Recipe(
            recipe_id=row.recipe_id,
            creator=creator,
            status=row.status or "draft",
            prep_time=row.prep_time or 0,
            portions=row.portion or 1,
        )

        # Le modèle métier actuel stocke les champs textuels dans `translations`.
        recipe.add_translation("fr", row.name, row.description or "")

        if ingredients:
            for ingredient_id, quantity in ingredients:
                # La BO impose quantity > 0
                if quantity is None or float(quantity) <= 0:
                    continue
                recipe.add_ingredient(
                    ingredient_id=int(ingredient_id),
                    quantity=float(quantity),
                )

        if tags:
            # Pas de BO Tag pour l'instant : on garde (tag_id, name).
            recipe.tags = [(int(tag_id), str(name)) for tag_id, name in tags]

        return recipe

    @staticmethod
    def _fetch_one_recipe(cur, recipe_id: int) -> RecipeRow | None:
        cur.execute(
            """
            SELECT
                recipe_id,
                fk_user_id,
                name,
                status,
                prep_time,
                portion,
                description,
                created_at
            FROM recipe
            WHERE recipe_id = %s
            """,
            (recipe_id,),
        )
        row = cur.fetchone()
        return RecipeRow(**row) if row else None

    # ---------------------------------------------------------------------
    # CRUD recipe
    # ---------------------------------------------------------------------

    @log
    def create_recipe(
        self,
        *,
        fk_user_id: int | None,
        name: str,
        status: str | None = "draft",
        prep_time: int | None = 0,
        portion: int | None = 1,
        description: str | None = None,
        ingredient_items: Iterable[tuple[int, float]] | None = None,
        tag_ids: Iterable[int] | None = None,
    ) -> Recipe:
        """Crée une recette (et optionnellement ses ingrédients/tags)."""

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recipe (fk_user_id, name, status, prep_time, portion, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING recipe_id
                    """,
                    (fk_user_id, name, status, prep_time, portion, description),
                )
                recipe_id = int(cur.fetchone()["recipe_id"])

                if ingredient_items:
                    self._bulk_upsert_recipe_ingredients(
                        cur, recipe_id, ingredient_items
                    )
                if tag_ids:
                    self._bulk_upsert_recipe_tags(cur, recipe_id, tag_ids)

                row = self._fetch_one_recipe(cur, recipe_id)
                if row is None:
                    raise RuntimeError("Insertion recette échouée (ligne introuvable).")

                ingredients = self.get_recipe_ingredients(recipe_id, cursor=cur)
                tags = self.get_recipe_tags(recipe_id, cursor=cur)

            conn.commit()
            return self._row_to_bo(row, ingredients=ingredients, tags=tags)
        except Exception:
            conn.rollback()
            raise

    @log
    def get_recipe_by_id(
        self, recipe_id: int, *, with_relations: bool = True
    ) -> Recipe | None:
        """Retourne une recette par id (avec relations si demandé)."""

        conn = DBConnection().connection
        with conn.cursor() as cur:
            row = self._fetch_one_recipe(cur, recipe_id)
            if row is None:
                return None

            if not with_relations:
                return self._row_to_bo(row)

            ingredients = self.get_recipe_ingredients(recipe_id, cursor=cur)
            tags = self.get_recipe_tags(recipe_id, cursor=cur)
            return self._row_to_bo(row, ingredients=ingredients, tags=tags)

    @log
    def list_recipes(
        self,
        *,
        fk_user_id: int | None = None,
        name_ilike: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Recipe]:
        """Liste des recettes (filtrables, sans charger les relations)."""

        limit = max(1, min(int(limit), 500))
        offset = max(0, int(offset))

        where_clauses: list[str] = []
        params: list[Any] = []

        if fk_user_id is not None:
            where_clauses.append("fk_user_id = %s")
            params.append(fk_user_id)
        if name_ilike:
            where_clauses.append("name ILIKE %s")
            params.append(f"%{name_ilike}%")

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    recipe_id,
                    fk_user_id,
                    name,
                    status,
                    prep_time,
                    portion,
                    description,
                    created_at
                FROM recipe
                {where_sql}
                ORDER BY created_at DESC, recipe_id DESC
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            rows = [RecipeRow(**r) for r in cur.fetchall()]

        return [self._row_to_bo(r) for r in rows]

    @log
    def update_recipe(
        self,
        recipe_id: int,
        *,
        name: str | None = None,
        status: str | None = None,
        prep_time: int | None = None,
        portion: int | None = None,
        description: str | None = None,
    ) -> Recipe | None:
        """Met à jour une recette (patch). Retourne la recette mise à jour."""

        fields: list[str] = []
        params: list[Any] = []

        if name is not None:
            fields.append("name = %s")
            params.append(name)
        if status is not None:
            fields.append("status = %s")
            params.append(status)
        if prep_time is not None:
            fields.append("prep_time = %s")
            params.append(prep_time)
        if portion is not None:
            fields.append("portion = %s")
            params.append(portion)
        if description is not None:
            fields.append("description = %s")
            params.append(description)

        if not fields:
            return self.get_recipe_by_id(recipe_id, with_relations=True)

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE recipe
                    SET {", ".join(fields)}
                    WHERE recipe_id = %s
                    """,
                    (*params, recipe_id),
                )
                if cur.rowcount == 0:
                    conn.rollback()
                    return None

                row = self._fetch_one_recipe(cur, recipe_id)
                if row is None:
                    conn.rollback()
                    return None

                ingredients = self.get_recipe_ingredients(recipe_id, cursor=cur)
                tags = self.get_recipe_tags(recipe_id, cursor=cur)

            conn.commit()
            return self._row_to_bo(row, ingredients=ingredients, tags=tags)
        except Exception:
            conn.rollback()
            raise

    @log
    def delete_recipe(self, recipe_id: int) -> bool:
        """Supprime une recette (cascade sur les tables de liaison)."""

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recipe WHERE recipe_id = %s", (recipe_id,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            raise

    # ---------------------------------------------------------------------
    # Relations : ingrédients
    # ---------------------------------------------------------------------

    @staticmethod
    def _bulk_upsert_recipe_ingredients(
        cur,
        recipe_id: int,
        ingredient_items: Iterable[tuple[int, float]],
    ) -> None:
        items = [(int(iid), float(qty)) for iid, qty in ingredient_items]
        if not items:
            return

        values_sql = ",".join(["(%s,%s,%s)"] * len(items))
        flat_params: list[Any] = []
        for ingredient_id, quantity in items:
            flat_params.extend([recipe_id, ingredient_id, quantity])

        cur.execute(
            f"""
            INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity)
            VALUES {values_sql}
            ON CONFLICT (fk_recipe_id, fk_ingredient_id)
            DO UPDATE SET quantity = EXCLUDED.quantity
            """,
            tuple(flat_params),
        )

    @log
    def add_or_update_ingredient(
        self, recipe_id: int, ingredient_id: int, quantity: float
    ) -> None:
        """Ajoute un ingrédient à la recette ou met à jour sa quantité."""

        if quantity <= 0:
            raise ValueError("La quantité doit être positive.")

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recipe_ingredient (fk_recipe_id, fk_ingredient_id, quantity)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (fk_recipe_id, fk_ingredient_id)
                    DO UPDATE SET quantity = EXCLUDED.quantity
                    """,
                    (recipe_id, ingredient_id, quantity),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @log
    def remove_ingredient(self, recipe_id: int, ingredient_id: int) -> bool:
        """Supprime un ingrédient d'une recette."""

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM recipe_ingredient
                    WHERE fk_recipe_id = %s AND fk_ingredient_id = %s
                    """,
                    (recipe_id, ingredient_id),
                )
                removed = cur.rowcount > 0
            conn.commit()
            return removed
        except Exception:
            conn.rollback()
            raise

    @log
    def replace_ingredients(
        self, recipe_id: int, ingredient_items: Iterable[tuple[int, float]]
    ) -> None:
        """Remplace complètement la liste d'ingrédients d'une recette."""

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM recipe_ingredient WHERE fk_recipe_id = %s",
                    (recipe_id,),
                )
                self._bulk_upsert_recipe_ingredients(cur, recipe_id, ingredient_items)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def get_recipe_ingredients(
        self, recipe_id: int, *, cursor=None
    ) -> list[tuple[int, float]]:
        """Retourne la liste (ingredient_id, quantity) d'une recette."""

        conn = DBConnection().connection
        should_close = cursor is None
        cur = cursor or conn.cursor()
        try:
            cur.execute(
                """
                SELECT fk_ingredient_id, quantity
                FROM recipe_ingredient
                WHERE fk_recipe_id = %s
                ORDER BY fk_ingredient_id
                """,
                (recipe_id,),
            )
            return [
                (int(r["fk_ingredient_id"]), float(r["quantity"]))
                for r in cur.fetchall()
            ]
        finally:
            if should_close:
                cur.close()

    # ---------------------------------------------------------------------
    # Relations : tags
    # ---------------------------------------------------------------------

    @staticmethod
    def _bulk_upsert_recipe_tags(cur, recipe_id: int, tag_ids: Iterable[int]) -> None:
        ids = [int(tag_id) for tag_id in tag_ids]
        if not ids:
            return

        values_sql = ",".join(["(%s,%s)"] * len(ids))
        flat_params: list[Any] = []
        for tag_id in ids:
            flat_params.extend([recipe_id, tag_id])

        cur.execute(
            f"""
            INSERT INTO recipe_tag (fk_recipe_id, fk_tag_id)
            VALUES {values_sql}
            ON CONFLICT (fk_recipe_id, fk_tag_id) DO NOTHING
            """,
            tuple(flat_params),
        )

    @log
    def add_tag(self, recipe_id: int, tag_id: int) -> None:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO recipe_tag (fk_recipe_id, fk_tag_id)
                    VALUES (%s, %s)
                    ON CONFLICT (fk_recipe_id, fk_tag_id) DO NOTHING
                    """,
                    (recipe_id, tag_id),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    @log
    def remove_tag(self, recipe_id: int, tag_id: int) -> bool:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM recipe_tag
                    WHERE fk_recipe_id = %s AND fk_tag_id = %s
                    """,
                    (recipe_id, tag_id),
                )
                removed = cur.rowcount > 0
            conn.commit()
            return removed
        except Exception:
            conn.rollback()
            raise

    @log
    def replace_tags(self, recipe_id: int, tag_ids: Iterable[int]) -> None:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM recipe_tag WHERE fk_recipe_id = %s", (recipe_id,)
                )
                self._bulk_upsert_recipe_tags(cur, recipe_id, tag_ids)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def get_recipe_tags(self, recipe_id: int, *, cursor=None) -> list[tuple[int, str]]:
        """Retourne la liste des tags (tag_id, name) d'une recette."""

        conn = DBConnection().connection
        should_close = cursor is None
        cur = cursor or conn.cursor()
        try:
            cur.execute(
                """
                SELECT t.tag_id, t.name
                FROM recipe_tag rt
                JOIN tag t ON t.tag_id = rt.fk_tag_id
                WHERE rt.fk_recipe_id = %s
                ORDER BY t.name
                """,
                (recipe_id,),
            )
            return [(int(r["tag_id"]), str(r["name"])) for r in cur.fetchall()]
        finally:
            if should_close:
                cur.close()

    # ---------------------------------------------------------------------
    # Recherche : Pour le service
    # ---------------------------------------------------------------------

    @log
    def find_recipes_by_ingredients(
        self,
        ingredients: list[str],
        *,
        limit: int = 10,
        max_missing: int = 0,
        strict_only: bool = False,
        dish_type: str | None = None,
        # ignore_pantry: bool = True,  # gardé pour compat, non utilisé sans table pantry
    ) -> list[Recipe]:
        """
        Recherche de recettes par ingrédients (approximative).
        - ingredients: liste de chaînes (noms d'ingrédients)
        - max_missing: tolérance (0 = strict)
        - strict_only: si True, force max_missing=0
        - dish_type: si fourni, filtre par tag (ex: "dessert")
        """

        ings = [s.strip() for s in ingredients if s and s.strip()]
        if not ings:
            return []

        limit = max(1, min(int(limit), 200))
        max_missing = max(0, int(max_missing))
        if strict_only:
            max_missing = 0

        # On match chaque terme avec ILIKE %term%
        like_terms = [f"%{s}%" for s in ings]
        n_terms = len(like_terms)

        tag_join = ""
        tag_where = ""
        params: list[Any] = []

        if dish_type:
            # Filtre sur tag.name (ex: dessert)
            tag_join = """
            JOIN recipe_tag rt_filter ON rt_filter.fk_recipe_id = r.recipe_id
            JOIN tag t_filter ON t_filter.tag_id = rt_filter.fk_tag_id
            """
            tag_where = "AND t_filter.name ILIKE %s"
            params.append(f"%{dish_type}%")

        conn = DBConnection().connection
        with conn.cursor() as cur:
            # 1) Trouver les recipes + matched_count
            # matched_count = nombre d'ingrédients distincts de la requête présents dans la recette
            # On compte un terme comme "matched" si la recette a au moins un ingrédient
            # dont le nom matche ce terme.
            cur.execute(
                f"""
                WITH matched AS (
                    SELECT
                        r.recipe_id,
                        COUNT(DISTINCT q.term) AS matched_count
                    FROM recipe r
                    {tag_join}
                    JOIN recipe_ingredient ri ON ri.fk_recipe_id = r.recipe_id
                    JOIN ingredient i ON i.ingredient_id = ri.fk_ingredient_id
                    JOIN (
                        SELECT UNNEST(%s::text[]) AS term
                    ) q ON i.name ILIKE q.term
                    WHERE 1=1
                    {tag_where}
                    GROUP BY r.recipe_id
                )
                SELECT
                    r.recipe_id,
                    r.fk_user_id,
                    r.name,
                    r.status,
                    r.prep_time,
                    r.portion,
                    r.description,
                    r.created_at,
                    m.matched_count
                FROM matched m
                JOIN recipe r ON r.recipe_id = m.recipe_id
                WHERE (%s - m.matched_count) <= %s
                ORDER BY m.matched_count DESC, r.created_at DESC, r.recipe_id DESC
                LIMIT %s
                """,
                (
                    like_terms,  # %s::text[]
                    *params,  # éventuellement dish_type
                    n_terms,  # %s (nb termes)
                    max_missing,  # %s (tolérance)
                    limit,  # %s (limit)
                ),
            )

            rows = cur.fetchall()

            # 2) Construire les Recipe (avec relations)
            recipes: list[Recipe] = []
            for r in rows:
                row = RecipeRow(
                    recipe_id=int(r["recipe_id"]),
                    fk_user_id=r["fk_user_id"],
                    name=str(r["name"]),
                    status=r["status"],
                    prep_time=r["prep_time"],
                    portion=r["portion"],
                    description=r["description"],
                    created_at=r["created_at"],
                )
                ingredients_rel = self.get_recipe_ingredients(row.recipe_id, cursor=cur)
                tags_rel = self.get_recipe_tags(row.recipe_id, cursor=cur)
                recipes.append(
                    self._row_to_bo(row, ingredients=ingredients_rel, tags=tags_rel)
                )

            return recipes
