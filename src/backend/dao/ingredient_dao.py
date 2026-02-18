from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from business_objects.ingredient import Ingredient
from business_objects.unit import Unit
from dao.db_connection import DBConnection
from utils.log_decorator import log


@dataclass(frozen=True, slots=True)
class IngredientRow:
    """Représentation typée d'une ligne issue de la table `ingredient`.

    Attributes:
        ingredient_id: Identifiant unique.
        name: Nom de l’ingrédient.
        unit: Valeur canonique stockée en base (ENUM unit_type).
    """

    ingredient_id: int
    name: str
    unit: str | None


class IngredientDAO:
    """DAO responsable des accès à `ingredient` et `ingredient_tag`.

    Cette classe gère :
        - CRUD des ingrédients
        - Gestion des relations avec les tags
    """

    # ==========================================================
    # Mapping DB -> BO
    # ==========================================================

    @staticmethod
    def _row_to_bo(row: IngredientRow, tag_ids: list[int] | None = None) -> Ingredient:
        """Transforme une ligne DB en objet métier.

        Args:
            row: Ligne issue de la base.
            tag_ids: Liste des tag_ids associés.

        Returns:
            Ingredient: Objet métier.
        """
        return Ingredient(
            id_ingredient=row.ingredient_id,
            name=row.name,
            unit=Unit.from_any(row.unit) if row.unit else Unit.PIECE,
            id_tags=tag_ids or [],
        )

    # ==========================================================
    # Gestion des tags
    # ==========================================================

    @staticmethod
    def _get_tag_ids(cur, ingredient_id: int) -> list[int]:
        """Récupère les tag_ids associés à un ingrédient."""
        cur.execute(
            """
            SELECT fk_tag_id
            FROM ingredient_tag
            WHERE fk_ingredient_id = %s
            ORDER BY fk_tag_id
            """,
            (ingredient_id,),
        )
        return [int(r["fk_tag_id"]) for r in cur.fetchall()]

    @staticmethod
    def _replace_tags(
        cur,
        ingredient_id: int,
        tag_ids: Iterable[int] | None,
    ) -> None:
        """Remplace entièrement les tags associés à un ingrédient."""
        cur.execute(
            "DELETE FROM ingredient_tag WHERE fk_ingredient_id = %s",
            (ingredient_id,),
        )

        if not tag_ids:
            return

        unique_ids = sorted({int(t) for t in tag_ids})

        cur.executemany(
            """
            INSERT INTO ingredient_tag (fk_ingredient_id, fk_tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            [(ingredient_id, tag_id) for tag_id in unique_ids],
        )

    # ==========================================================
    # CRUD
    # ==========================================================

    @log
    def create_ingredient(
        self,
        *,
        name: str,
        unit: Unit | str | None = None,
        tag_ids: Iterable[int] | None = None,
    ) -> Ingredient:
        """Crée un nouvel ingrédient.

        Args:
            name: Nom de l’ingrédient.
            unit: Unité (Unit ou string libre).
            tag_ids: Liste optionnelle de tag_ids.

        Returns:
            Ingredient: Objet créé.
        """
        parsed_unit = Unit.from_any(unit) if unit else None
        unit_value = parsed_unit.value if parsed_unit else None

        conn = DBConnection().connection

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ingredient (name, unit)
                    VALUES (%s, %s)
                    RETURNING ingredient_id
                    """,
                    (name, unit_value),
                )

                ingredient_id = int(cur.fetchone()["ingredient_id"])

                if tag_ids is not None:
                    self._replace_tags(cur, ingredient_id, tag_ids)

                cur.execute(
                    """
                    SELECT ingredient_id, name, unit
                    FROM ingredient
                    WHERE ingredient_id = %s
                    """,
                    (ingredient_id,),
                )

                row = IngredientRow(**cur.fetchone())
                tags = self._get_tag_ids(cur, ingredient_id)

            conn.commit()
            return self._row_to_bo(row, tags)

        except Exception:
            conn.rollback()
            raise

    @log
    def get_ingredient_by_id(
        self,
        ingredient_id: int,
        with_tags: bool = True,
    ) -> Ingredient | None:
        """Récupère un ingrédient par son identifiant."""
        conn = DBConnection().connection

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ingredient_id, name, unit
                FROM ingredient
                WHERE ingredient_id = %s
                """,
                (ingredient_id,),
            )

            row = cur.fetchone()
            if not row:
                return None

            row_obj = IngredientRow(**row)
            tags = self._get_tag_ids(cur, ingredient_id) if with_tags else []

            return self._row_to_bo(row_obj, tags)

    @log
    def get_ingredient_by_name(
        self,
        name: str,
        with_tags: bool = True,
    ) -> Ingredient | None:
        """Récupère un ingrédient par son nom (insensible à la casse).

        La recherche est effectuée avec LOWER(name) = LOWER(%s).
        Si plusieurs ingrédients ont le même nom, le plus ancien
        (plus petit ingredient_id) est retourné.

        Args:
            name: Nom exact recherché.
            with_tags: Charge les tags si True.

        Returns:
            Ingredient | None: Objet trouvé ou None si inexistant.
        """
        conn = DBConnection().connection

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ingredient_id, name, unit
                FROM ingredient
                WHERE LOWER(name) = LOWER(%s)
                ORDER BY ingredient_id ASC
                LIMIT 1
                """,
                (name,),
            )

            row = cur.fetchone()
            if not row:
                return None

            row_obj = IngredientRow(**row)

            tags = self._get_tag_ids(cur, row_obj.ingredient_id) if with_tags else []

            return self._row_to_bo(row_obj, tags)

    @log
    def delete_ingredient(self, ingredient_id: int) -> bool:
        """Supprime un ingrédient.

        Args:
            ingredient_id: Identifiant à supprimer.

        Returns:
            bool: True si suppression effectuée.
        """
        conn = DBConnection().connection

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM ingredient WHERE ingredient_id = %s",
                    (ingredient_id,),
                )
                deleted = cur.rowcount > 0

            conn.commit()
            return deleted

        except Exception:
            conn.rollback()
            raise

    @log
    def list_ingredients(self, with_tags: bool = True) -> list[Ingredient]:
        """
        Récupère la liste complète des ingrédients présents en base.

        Args:
            with_tags (bool):
                Si True, charge également les identifiants des tags associés
                à chaque ingrédient.

        Returns:
            list[Ingredient]:
                Liste d'objets métier Ingredient triés par nom.
        """
        # Connexion à la base via le singleton DBConnection
        conn = DBConnection().connection

        with conn.cursor() as cur:
            # On récupère tous les ingrédients
            cur.execute(
                """
                SELECT ingredient_id, name, unit
                FROM ingredient
                ORDER BY name ASC
                """
            )

            rows = cur.fetchall()

            ingredients: list[Ingredient] = []

            # Transformation des lignes SQL en objets métier
            for r in rows:
                row_obj = IngredientRow(**r)

                # Chargement optionnel des tags associés
                tags = (
                    self._get_tag_ids(cur, row_obj.ingredient_id) if with_tags else []
                )

                ingredients.append(self._row_to_bo(row_obj, tags))

            return ingredients
