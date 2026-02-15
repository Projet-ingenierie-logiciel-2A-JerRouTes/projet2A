from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.backend.dao.db_connection import DBConnection
from src.backend.utils.log_decorator import log


_UNSET = object()


@dataclass(frozen=True, slots=True)
class StockItemRow:
    """Représentation typée d'une ligne de la table `stock_item`.

    Attributes:
        stock_item_id: Identifiant unique du lot.
        fk_stock_id: Identifiant du stock.
        fk_ingredient_id: Identifiant de l'ingrédient.
        quantity: Quantité disponible.
        expiration_date: Date de péremption (peut être NULL).
        created_at: Date de création en base.
    """

    stock_item_id: int
    fk_stock_id: int
    fk_ingredient_id: int
    quantity: Any
    expiration_date: date | None
    created_at: Any


class StockItemDAO:
    """DAO responsable de la table `stock_item` (gestion des lots)."""

    # ------------------------------------------------------------------
    # Lectures
    # ------------------------------------------------------------------

    @log
    def get_stock_item_by_id(self, stock_item_id: int) -> StockItemRow | None:
        """Récupère un lot par son identifiant.

        Args:
            stock_item_id: Identifiant du lot.

        Returns:
            StockItemRow | None: Lot si trouvé, sinon None.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT stock_item_id, fk_stock_id, fk_ingredient_id, quantity, expiration_date, created_at
                FROM stock_item
                WHERE stock_item_id = %s
                """,
                (stock_item_id,),
            )
            row = cur.fetchone()
            return StockItemRow(**row) if row else None

    @log
    def list_stock_items(
        self,
        *,
        stock_id: int,
        ingredient_id: int | None = None,
        order_fefo: bool = True,
    ) -> list[StockItemRow]:
        """Liste les lots d'un stock (optionnellement filtrés par ingrédient).

        Args:
            stock_id: Identifiant du stock.
            ingredient_id: Filtre optionnel sur un ingrédient.
            order_fefo: Si True, trie FEFO (expiration_date ASC NULLS LAST,
                puis created_at ASC, puis stock_item_id ASC).

        Returns:
            list[StockItemRow]: Liste des lots.
        """
        where = ["fk_stock_id = %s"]
        params: list[Any] = [stock_id]

        if ingredient_id is not None:
            where.append("fk_ingredient_id = %s")
            params.append(ingredient_id)

        order_sql = ""
        if order_fefo:
            order_sql = """
            ORDER BY
                expiration_date ASC NULLS LAST,
                created_at ASC,
                stock_item_id ASC
            """

        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT stock_item_id, fk_stock_id, fk_ingredient_id, quantity, expiration_date, created_at
                FROM stock_item
                WHERE {" AND ".join(where)}
                {order_sql}
                """,
                tuple(params),
            )
            return [StockItemRow(**r) for r in cur.fetchall()]

    # ------------------------------------------------------------------
    # Écritures (CRUD lots)
    # ------------------------------------------------------------------

    @log
    def create_stock_item(
        self,
        *,
        stock_id: int,
        ingredient_id: int,
        quantity: float,
        expiration_date: date | None,
    ) -> int:
        """Crée un nouveau lot dans un stock.

        Args:
            stock_id: Identifiant du stock.
            ingredient_id: Identifiant de l'ingrédient.
            quantity: Quantité du lot (>= 0).
            expiration_date: Date de péremption (peut être None).

        Returns:
            int: Identifiant du lot créé (stock_item_id).
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO stock_item (fk_stock_id, fk_ingredient_id, quantity, expiration_date)
                    VALUES (%s, %s, %s, %s)
                    RETURNING stock_item_id
                    """,
                    (stock_id, ingredient_id, quantity, expiration_date),
                )
                lot_id = int(cur.fetchone()["stock_item_id"])
            conn.commit()
            return lot_id
        except Exception:
            conn.rollback()
            raise

    @log
    def update_stock_item(
        self,
        stock_item_id: int,
        *,
        quantity: float | None = None,
        expiration_date: date | None | object = _UNSET,
    ) -> StockItemRow | None:
        """Met à jour un lot existant.

        Notes:
            - `quantity=None` => quantité non modifiée
            - `expiration_date=_UNSET` (défaut) => date non modifiée
            - `expiration_date=None` explicite => met expiration_date à NULL

        Args:
            stock_item_id: Identifiant du lot.
            quantity: Nouvelle quantité (>= 0).
            expiration_date: Nouvelle date (None autorisé).

        Returns:
            StockItemRow | None: Lot mis à jour, ou None si inexistant.
        """
        fields: list[str] = []
        params: list[Any] = []

        if quantity is not None:
            fields.append("quantity = %s")
            params.append(quantity)

        if expiration_date is not _UNSET:
            fields.append("expiration_date = %s")
            params.append(expiration_date)

        if not fields:
            return self.get_stock_item_by_id(stock_item_id)

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE stock_item
                    SET {", ".join(fields)}
                    WHERE stock_item_id = %s
                    """,
                    (*params, stock_item_id),
                )
                updated = self.get_stock_item_by_id(stock_item_id)
            conn.commit()
            return updated
        except Exception:
            conn.rollback()
            raise

    @log
    def delete_stock_item(self, stock_item_id: int) -> bool:
        """Supprime un lot.

        Args:
            stock_item_id: Identifiant du lot.

        Returns:
            bool: True si supprimé, False sinon.
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM stock_item WHERE stock_item_id = %s",
                    (stock_item_id,),
                )
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            raise

    # ------------------------------------------------------------------
    # Consommation FEFO (transactionnelle)
    # ------------------------------------------------------------------

    @log
    def consume_quantity_fefo(
        self,
        *,
        stock_id: int,
        ingredient_id: int,
        quantity_to_consume: float,
    ) -> None:
        """Consomme une quantité en base en respectant FEFO.

        Algorithme :
            - Sélectionne les lots du (stock, ingredient) triés FEFO
            - Décrémente lot par lot
            - Supprime les lots vidés

        Args:
            stock_id: Identifiant du stock.
            ingredient_id: Identifiant de l'ingrédient.
            quantity_to_consume: Quantité à consommer (> 0).

        Raises:
            ValueError: Si quantity_to_consume <= 0 ou stock insuffisant.
        """
        if quantity_to_consume <= 0:
            raise ValueError("La quantité à consommer doit être strictement positive.")

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT stock_item_id, quantity
                    FROM stock_item
                    WHERE fk_stock_id = %s AND fk_ingredient_id = %s
                    ORDER BY expiration_date ASC NULLS LAST, created_at ASC, stock_item_id ASC
                    FOR UPDATE
                    """,
                    (stock_id, ingredient_id),
                )
                rows = cur.fetchall()

                total_available = sum(float(r["quantity"]) for r in rows)
                if quantity_to_consume > total_available:
                    raise ValueError(
                        f"Stock insuffisant (ingredient_id={ingredient_id}): "
                        f"demande={quantity_to_consume}, disponible={total_available}."
                    )

                remaining = float(quantity_to_consume)

                for r in rows:
                    lot_id = int(r["stock_item_id"])
                    lot_qty = float(r["quantity"])

                    if remaining <= 0:
                        break

                    if lot_qty > remaining:
                        cur.execute(
                            """
                            UPDATE stock_item
                            SET quantity = %s
                            WHERE stock_item_id = %s
                            """,
                            (lot_qty - remaining, lot_id),
                        )
                        remaining = 0.0
                    else:
                        cur.execute(
                            "DELETE FROM stock_item WHERE stock_item_id = %s",
                            (lot_id,),
                        )
                        remaining -= lot_qty

            conn.commit()
        except Exception:
            conn.rollback()
            raise
