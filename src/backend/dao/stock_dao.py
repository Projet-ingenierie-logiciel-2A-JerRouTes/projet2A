from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from src.backend.business_objects.stock import Stock
from src.backend.dao.db_connection import DBConnection
from src.backend.utils.log_decorator import log


@dataclass(frozen=True, slots=True)
class StockRow:
    """Représentation typée d'une ligne de la table `stock`.

    Attributes:
        stock_id: Identifiant du stock.
        name: Nom du stock.
    """

    stock_id: int
    name: str


@dataclass(frozen=True, slots=True)
class StockItemLiteRow:
    """Représentation typée minimale d'un lot pour construire la BO Stock.

    Attributes:
        stock_item_id: Identifiant du lot.
        fk_ingredient_id: Identifiant ingrédient.
        quantity: Quantité.
        expiration_date: Date de péremption (peut être NULL).
    """

    stock_item_id: int
    fk_ingredient_id: int
    quantity: Any
    expiration_date: date | None


class StockDAO:
    """DAO pour `stock` + `user_stock` + lecture des lots `stock_item`.

    Notes:
        - L'ajout/suppression de lots se fait via StockItemDAO (ou via un service).
        - Les règles de droits (user propriétaire du stock) doivent vivre dans la couche service.
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _fetch_one_stock(cur, stock_id: int) -> StockRow | None:
        cur.execute(
            """
            SELECT stock_id, name
            FROM stock
            WHERE stock_id = %s
            """,
            (stock_id,),
        )
        row = cur.fetchone()
        return StockRow(**row) if row else None

    @staticmethod
    def _fetch_stock_items(cur, stock_id: int) -> list[StockItemLiteRow]:
        cur.execute(
            """
            SELECT stock_item_id, fk_ingredient_id, quantity, expiration_date
            FROM stock_item
            WHERE fk_stock_id = %s
            ORDER BY expiration_date ASC NULLS LAST, created_at ASC, stock_item_id ASC
            """,
            (stock_id,),
        )
        return [StockItemLiteRow(**r) for r in cur.fetchall()]

    @classmethod
    def _row_to_bo(
        cls,
        row: StockRow,
        *,
        item_rows: list[StockItemLiteRow] | None = None,
    ) -> Stock:
        stock = Stock(id_stock=int(row.stock_id), nom=str(row.name))

        if item_rows:
            for r in item_rows:
                qty = 0.0 if r.quantity is None else float(r.quantity)
                exp = r.expiration_date or date.max  # BO exige une date
                stock.add_item(
                    id_ingredient=int(r.fk_ingredient_id),
                    id_lot=int(r.stock_item_id),
                    quantity=qty,
                    expiry_date=exp,
                )
        return stock

    # ------------------------------------------------------------------
    # CRUD stock
    # ------------------------------------------------------------------

    @log
    def create_stock(self, *, name: str) -> Stock:
        """Crée un stock.

        Args:
            name: Nom du stock.

        Returns:
            Stock: Stock créé (sans lots).
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO stock (name)
                    VALUES (%s)
                    RETURNING stock_id
                    """,
                    (name,),
                )
                stock_id = int(cur.fetchone()["stock_id"])
                row = self._fetch_one_stock(cur, stock_id)
                if row is None:
                    raise RuntimeError("Insertion stock échouée (row=None).")
            conn.commit()
            return self._row_to_bo(row)
        except Exception:
            conn.rollback()
            raise

    @log
    def get_stock_by_id(
        self, stock_id: int, *, with_items: bool = True
    ) -> Stock | None:
        """Récupère un stock par id.

        Args:
            stock_id: Identifiant du stock.
            with_items: Si True, charge les lots (stock_item) dans la BO.

        Returns:
            Stock | None: Stock trouvé ou None.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            row = self._fetch_one_stock(cur, stock_id)
            if row is None:
                return None
            items = self._fetch_stock_items(cur, stock_id) if with_items else []
            return self._row_to_bo(row, item_rows=items)

    @log
    def list_stocks(
        self,
        *,
        name_ilike: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Stock]:
        """Liste les stocks (sans charger les lots).

        Args:
            name_ilike: Filtre optionnel sur le nom.
            limit: Taille max.
            offset: Offset pagination.

        Returns:
            list[Stock]: Liste des stocks.
        """
        limit = max(1, min(int(limit), 500))
        offset = max(0, int(offset))

        where_sql = ""
        params: list[Any] = []
        if name_ilike:
            where_sql = "WHERE name ILIKE %s"
            params.append(f"%{name_ilike}%")

        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT stock_id, name
                FROM stock
                {where_sql}
                ORDER BY name ASC, stock_id ASC
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            rows = [StockRow(**r) for r in cur.fetchall()]
        return [self._row_to_bo(r) for r in rows]

    @log
    def update_stock(self, stock_id: int, *, name: str | None = None) -> Stock | None:
        """Met à jour un stock.

        Args:
            stock_id: Identifiant du stock.
            name: Nouveau nom.

        Returns:
            Stock | None: Stock mis à jour ou None si inexistant.
        """
        if name is None:
            return self.get_stock_by_id(stock_id, with_items=True)

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE stock
                    SET name = %s
                    WHERE stock_id = %s
                    """,
                    (name, stock_id),
                )
                row = self._fetch_one_stock(cur, stock_id)
                if row is None:
                    conn.commit()
                    return None
                items = self._fetch_stock_items(cur, stock_id)
            conn.commit()
            return self._row_to_bo(row, item_rows=items)
        except Exception:
            conn.rollback()
            raise

    @log
    def delete_stock(self, stock_id: int) -> bool:
        """Supprime un stock.

        Args:
            stock_id: Identifiant du stock.

        Returns:
            bool: True si supprimé.
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM stock WHERE stock_id = %s", (stock_id,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        except Exception:
            conn.rollback()
            raise

    # ------------------------------------------------------------------
    # user_stock (association user <-> stock)
    # ------------------------------------------------------------------

    @log
    def add_stock_to_user(self, *, user_id: int, stock_id: int) -> bool:
        """Associe un stock à un utilisateur.

        Args:
            user_id: Identifiant utilisateur.
            stock_id: Identifiant stock.

        Returns:
            bool: True si insertion, False si déjà existant.
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_stock (fk_user_id, fk_stock_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (user_id, stock_id),
                )
                inserted = cur.rowcount > 0
            conn.commit()
            return inserted
        except Exception:
            conn.rollback()
            raise

    @log
    def list_user_stocks(
        self,
        user_id: int,
        *,
        name_ilike: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Stock]:
        """Liste les stocks d'un utilisateur (sans charger les lots).

        Args:
            user_id: Identifiant utilisateur.
            name_ilike: Filtre optionnel sur le nom du stock (ILIKE).
            limit: Taille max (clampée).
            offset: Offset pagination.

        Returns:
            list[Stock]: Stocks associés à l'utilisateur.
        """
        limit = max(1, min(int(limit), 500))
        offset = max(0, int(offset))

        where = ["us.fk_user_id = %s"]
        params: list[Any] = [user_id]

        if name_ilike:
            where.append("s.name ILIKE %s")
            params.append(f"%{name_ilike}%")

        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT s.stock_id, s.name
                FROM stock s
                JOIN user_stock us ON us.fk_stock_id = s.stock_id
                WHERE {" AND ".join(where)}
                ORDER BY s.name ASC, s.stock_id ASC
                LIMIT %s OFFSET %s
                """,
                (*params, limit, offset),
            )
            rows = [StockRow(**r) for r in cur.fetchall()]
        return [self._row_to_bo(r) for r in rows]

    @log
    def get_user_stock_by_name(
        self,
        *,
        user_id: int,
        name: str,
        with_items: bool = False,
    ) -> Stock | None:
        """Récupère un stock d'un utilisateur par son nom (insensible à la casse).

        Args:
            user_id: Identifiant utilisateur.
            name: Nom exact du stock (casse ignorée).
            with_items: Si True, charge les lots dans la BO.

        Returns:
            Stock | None: Stock trouvé ou None.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.stock_id, s.name
                FROM stock s
                JOIN user_stock us ON us.fk_stock_id = s.stock_id
                WHERE us.fk_user_id = %s AND LOWER(s.name) = LOWER(%s)
                ORDER BY s.stock_id ASC
                LIMIT 1
                """,
                (user_id, name),
            )
            row = cur.fetchone()
            if not row:
                return None

            stock_row = StockRow(**row)
            items = (
                self._fetch_stock_items(cur, stock_row.stock_id) if with_items else []
            )
            return self._row_to_bo(stock_row, item_rows=items)
