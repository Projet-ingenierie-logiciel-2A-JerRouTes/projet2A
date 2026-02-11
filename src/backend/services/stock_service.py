from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.backend.dao.db_connection import DBConnection
from src.backend.dao.ingredient_dao import IngredientDAO
from src.backend.dao.stock_dao import StockDAO
from src.backend.dao.stock_item_dao import StockItemDAO, StockItemRow
from src.backend.utils.log_decorator import log


class StockServiceError(Exception):
    """Erreur de base pour la couche service stock."""


class NotFoundError(StockServiceError):
    """Ressource introuvable."""


class ForbiddenError(StockServiceError):
    """Accès interdit (droits insuffisants)."""


class ValidationError(StockServiceError):
    """Données invalides."""


@dataclass(frozen=True, slots=True)
class ConsumeResult:
    """Résultat d'une consommation de stock.

    Attributes:
        stock_id: Identifiant du stock.
        ingredient_id: Identifiant de l'ingrédient.
        consumed_quantity: Quantité effectivement consommée.
    """

    stock_id: int
    ingredient_id: int
    consumed_quantity: float


class StockService:
    """Service métier pour relier stock, lots (stock_item) et ingrédients.

    Cette couche gère :
        - Droits (ownership via user_stock)
        - Validations (quantités, existence d'ingrédients)
        - Orchestration des DAO (StockDAO, StockItemDAO, IngredientDAO)

    Notes:
        - Les DAO font les commits/rollbacks sur leurs opérations.
        - Les règles de droits sont centralisées ici (pas dans les DAO).
    """

    def __init__(
        self,
        *,
        stock_dao: StockDAO | None = None,
        stock_item_dao: StockItemDAO | None = None,
        ingredient_dao: IngredientDAO | None = None,
    ) -> None:
        """Initialise le service avec injection possible des DAO."""
        self._stock_dao = stock_dao or StockDAO()
        self._stock_item_dao = stock_item_dao or StockItemDAO()
        self._ingredient_dao = ingredient_dao or IngredientDAO()

    # ------------------------------------------------------------------
    # Helpers droits / existence
    # ------------------------------------------------------------------

    @staticmethod
    def _assert_positive(quantity: float, field_name: str = "quantity") -> None:
        """Valide qu'une quantité est strictement positive."""
        try:
            q = float(quantity)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError(f"{field_name} doit être un nombre.") from exc

        if q <= 0:
            raise ValidationError(f"{field_name} doit être strictement positive.")

    def _user_owns_stock(self, *, user_id: int, stock_id: int) -> bool:
        """Vérifie si un utilisateur est propriétaire d'un stock via user_stock.

        Args:
            user_id: Identifiant utilisateur.
            stock_id: Identifiant stock.

        Returns:
            bool: True si l'utilisateur possède le stock.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM user_stock
                WHERE fk_user_id = %s AND fk_stock_id = %s
                LIMIT 1
                """,
                (user_id, stock_id),
            )
            return cur.fetchone() is not None

    def _require_stock_ownership(self, *, user_id: int, stock_id: int) -> None:
        """Lève une exception si l'utilisateur ne possède pas le stock."""
        if not self._user_owns_stock(user_id=user_id, stock_id=stock_id):
            raise ForbiddenError("Vous n'avez pas accès à ce stock.")

    def _require_stock_exists(self, stock_id: int) -> None:
        """Lève une exception si le stock n'existe pas."""
        if self._stock_dao.get_stock_by_id(stock_id, with_items=False) is None:
            raise NotFoundError("Stock introuvable.")

    def _require_ingredient_exists(self, ingredient_id: int) -> None:
        """Lève une exception si l'ingrédient n'existe pas."""
        if (
            self._ingredient_dao.get_ingredient_by_id(ingredient_id, with_tags=False)
            is None
        ):
            raise NotFoundError("Ingrédient introuvable.")

    # ------------------------------------------------------------------
    # API métier (stocks)
    # ------------------------------------------------------------------

    @log
    def create_stock_for_user(self, *, user_id: int, name: str) -> int:
        """Crée un stock et l'associe immédiatement à un utilisateur.

        Args:
            user_id: Identifiant utilisateur.
            name: Nom du stock.

        Returns:
            int: Identifiant du stock créé.
        """
        stock = self._stock_dao.create_stock(name=name)
        self._stock_dao.add_stock_to_user(user_id=user_id, stock_id=stock.id_stock)
        return stock.id_stock

    @log
    def get_user_stock_by_name(
        self, *, user_id: int, name: str, with_items: bool = False
    ):
        """Récupère un stock appartenant au user par son nom.

        Args:
            user_id: Identifiant utilisateur.
            name: Nom exact (casse ignorée).
            with_items: Charge les lots si True.

        Returns:
            Stock | None: Le stock si trouvé, sinon None.
        """
        return self._stock_dao.get_user_stock_by_name(
            user_id=user_id, name=name, with_items=with_items
        )

    # ------------------------------------------------------------------
    # API métier (lots)
    # ------------------------------------------------------------------

    @log
    def add_lot(
        self,
        *,
        user_id: int,
        stock_id: int,
        ingredient_id: int,
        quantity: float,
        expiration_date: date | None = None,
    ) -> int:
        """Ajoute un lot (stock_item) à un stock appartenant à l'utilisateur.

        Args:
            user_id: Identifiant utilisateur.
            stock_id: Identifiant du stock.
            ingredient_id: Identifiant de l'ingrédient.
            quantity: Quantité à ajouter (> 0).
            expiration_date: Date de péremption (optionnelle).

        Returns:
            int: Identifiant du lot créé (stock_item_id).
        """
        self._assert_positive(quantity, "quantity")

        self._require_stock_exists(stock_id)
        self._require_stock_ownership(user_id=user_id, stock_id=stock_id)
        self._require_ingredient_exists(ingredient_id)

        return self._stock_item_dao.create_stock_item(
            stock_id=stock_id,
            ingredient_id=ingredient_id,
            quantity=float(quantity),
            expiration_date=expiration_date,
        )

    @log
    def list_lots(
        self,
        *,
        user_id: int,
        stock_id: int,
        ingredient_id: int | None = None,
    ) -> list[StockItemRow]:
        """Liste les lots d'un stock appartenant à l'utilisateur.

        Args:
            user_id: Identifiant utilisateur.
            stock_id: Identifiant stock.
            ingredient_id: Filtre optionnel sur un ingrédient.

        Returns:
            list[StockItemRow]: Lots triés FEFO.
        """
        self._require_stock_exists(stock_id)
        self._require_stock_ownership(user_id=user_id, stock_id=stock_id)

        return self._stock_item_dao.list_stock_items(
            stock_id=stock_id,
            ingredient_id=ingredient_id,
            order_fefo=True,
        )

    @log
    def delete_lot(self, *, user_id: int, stock_item_id: int) -> bool:
        """Supprime un lot si l'utilisateur possède le stock associé.

        Args:
            user_id: Identifiant utilisateur.
            stock_item_id: Identifiant du lot.

        Returns:
            bool: True si supprimé.

        Raises:
            NotFoundError: Si le lot n'existe pas.
            ForbiddenError: Si le user ne possède pas le stock.
        """
        lot = self._stock_item_dao.get_stock_item_by_id(stock_item_id)
        if lot is None:
            raise NotFoundError("Lot introuvable.")

        self._require_stock_ownership(user_id=user_id, stock_id=lot.fk_stock_id)
        return self._stock_item_dao.delete_stock_item(stock_item_id)

    @log
    def consume_fefo(
        self,
        *,
        user_id: int,
        stock_id: int,
        ingredient_id: int,
        quantity: float,
    ) -> ConsumeResult:
        """Consomme une quantité d'un ingrédient via FEFO sur un stock.

        Args:
            user_id: Identifiant utilisateur.
            stock_id: Identifiant stock.
            ingredient_id: Identifiant ingrédient.
            quantity: Quantité à consommer (> 0).

        Returns:
            ConsumeResult: Résumé de l'opération.

        Raises:
            ValidationError: Si quantity <= 0
            ForbiddenError: Si stock n'appartient pas au user
            NotFoundError: Si stock/ingrédient n'existent pas
            ValueError: Si stock insuffisant (propagé depuis DAO)
        """
        self._assert_positive(quantity, "quantity")

        self._require_stock_exists(stock_id)
        self._require_stock_ownership(user_id=user_id, stock_id=stock_id)
        self._require_ingredient_exists(ingredient_id)

        # Transaction FEFO gérée dans le DAO (FOR UPDATE)
        self._stock_item_dao.consume_quantity_fefo(
            stock_id=stock_id,
            ingredient_id=ingredient_id,
            quantity_to_consume=float(quantity),
        )

        return ConsumeResult(
            stock_id=stock_id,
            ingredient_id=ingredient_id,
            consumed_quantity=float(quantity),
        )
