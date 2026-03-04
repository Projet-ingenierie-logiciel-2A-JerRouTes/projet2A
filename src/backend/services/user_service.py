from __future__ import annotations

from dataclasses import dataclass
import secrets
import string

from business_objects.user import User
from dao.user_dao import UserDAO, UserRow

# ---------------------------------------------------------------------
# Exceptions "métier"
# ---------------------------------------------------------------------
from exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from utils.log_decorator import log
from utils.securite import check_password, hash_password


class UserServiceError(Exception):
    """Base des erreurs du service user."""


# class UserAlreadyExistsError(UserServiceError):
#    """Email ou username déjà utilisé."""


# class InvalidCredentialsError(UserServiceError):
#     """Identifiants invalides."""


# class UserNotFoundError(UserServiceError):
#    """Utilisateur introuvable."""
#    pass


# class InvalidPasswordError(Exception):
#    """Exception levée quand le mot de passe est incorrect."""
#    pass


# ---------------------------------------------------------------------
# DTO (optionnel mais pratique)
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User


# ---------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------


class UserService:
    def __init__(self, user_dao: UserDAO | None = None) -> None:
        self._user_dao = user_dao or UserDAO()

    # --------------------------------------------------------------
    # Lecture
    # --------------------------------------------------------------

    @log
    def get_user(self, user_id: int) -> User:
        user = self._user_dao.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")
        return user

    @log
    def get_user_row_by_email(self, email: str) -> UserRow:
        row = self._user_dao.get_user_row_by_email(email)
        if row is None:
            raise UserNotFoundError("Aucun utilisateur avec cet email.")
        return row

    # --------------------------------------------------------------
    # Récupération tous les utilisateurs
    # --------------------------------------------------------------

    @log
    def get_all_users(self, limit: int | None = None) -> list[User]:
        """
        Récupère la liste des utilisateurs.

        :param limit: Nombre maximal d'utilisateurs à récupérer (optionnel)
        """
        return self._user_dao.get_all_users(limit=limit)

    # --------------------------------------------------------------
    # Inscription / Auth
    # --------------------------------------------------------------

    @log
    def register(
        self,
        *,
        username: str,
        email: str,
        password: str,
        status: str = "user",
    ) -> User:
        # Unicité métier : username + email
        if self._user_dao.get_user_row_by_email(email) is not None:
            raise UserEmailAlreadyExistsError("Email déjà utilisé.")
        if self._user_dao.get_user_row_by_username(username) is not None:
            raise UserAlreadyExistsError("Nom d’utilisateur déjà utilisé.")

        pw_hash = hash_password(password)

        return self._user_dao.create_user(
            username=username,
            email=email,
            password_hash=pw_hash,
            status=status,
        )

    @log
    def authenticate(self, *, login: str, password: str) -> AuthResult:
        """
        Authentifie un user via email OU username (champ login).
        - Identifiants invalides => InvalidCredentialsError (générique).
        - Incohérence DB (row existe mais user métier absent) => UserNotFoundError.
        """
        # 1) Recherche de l'utilisateur
        row = self._user_dao.get_user_row_by_email(login)
        if row is None:
            row = self._user_dao.get_user_row_by_username(login)

        # 2) Aucun user correspondant
        if row is None:
            raise InvalidCredentialsError("Identifiants invalides.")

        # 3) Mauvais mot de passe
        if not check_password(password, row.password_hash):
            raise InvalidCredentialsError("Identifiants invalides.")

        # 4) Récupération de l'objet métier
        user = self._user_dao.get_user_by_id(row.user_id)
        if user is None:
            raise UserNotFoundError("Utilisateur introuvable en base de données.")

        return AuthResult(user=user)

    # --------------------------------------------------------------
    # Mise à jour
    # --------------------------------------------------------------

    @log
    def update_profile(
        self,
        user_id: int,
        *,
        username: str | None = None,
        email: str | None = None,
        status: str | None = None,
    ) -> User:
        # Check unicité si on change email/username
        if email is not None:
            existing = self._user_dao.get_user_row_by_email(email)
            if existing is not None and existing.user_id != user_id:
                raise UserAlreadyExistsError("Email déjà utilisé.")

        if username is not None:
            existing = self._user_dao.get_user_row_by_username(username)
            if existing is not None and existing.user_id != user_id:
                raise UserAlreadyExistsError("Nom d’utilisateur déjà utilisé.")

        updated = self._user_dao.update_user(
            user_id,
            username=username,
            email=email,
            status=status,
        )
        if updated is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")
        return updated

    @log
    def change_password(
        self,
        *,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> None:
        row = self._user_dao.get_user_row_by_id(user_id)
        if row is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

        if not check_password(old_password, row.password_hash):
            raise InvalidCredentialsError("Ancien mot de passe incorrect.")

        new_hash = hash_password(new_password)

        updated = self._user_dao.update_user(user_id, password_hash=new_hash)
        if updated is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

    # --------------------------------------------------------------
    # Suppression
    # --------------------------------------------------------------

    @log
    def delete_user(self, user_id: int) -> None:
        ok = self._user_dao.delete_user(user_id)
        if not ok:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

    @log
    def update_user_admin_or_self(
        self,
        *,
        requester_id: int,
        requester_is_admin: bool,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        old_password: str | None = None,
        new_password: str | None = None,
    ) -> User:
        """
        Met à jour un ou plusieurs attributs d'un utilisateur.

        - Admin: peut modifier n'importe quel utilisateur.
        - User: peut modifier uniquement ses propres informations.
        - Changement de mot de passe:
            - Admin: peut changer sans old_password (reset)
            - User: doit fournir old_password
        """
        # Droits
        if not requester_is_admin and requester_id != user_id:
            raise InvalidCredentialsError(
                "Vous ne pouvez modifier que votre propre compte."
            )

        # Récupération row DB pour validations + password
        row = self._user_dao.get_user_row_by_id(user_id)
        if row is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

        # Validation unicité (on réutilise ton update_profile mais ici on gère aussi le mdp)
        if email is not None:
            existing = self._user_dao.get_user_row_by_email(email)
            if existing is not None and existing.user_id != user_id:
                raise UserEmailAlreadyExistsError("Email déjà utilisé.")

        if username is not None:
            existing = self._user_dao.get_user_row_by_username(username)
            if existing is not None and existing.user_id != user_id:
                raise UserAlreadyExistsError("Nom d’utilisateur déjà utilisé.")

        # Gestion mot de passe (optionnelle)
        password_hash: str | None = None
        if new_password is not None:
            # Si pas admin, old_password obligatoire
            if not requester_is_admin and (
                old_password is None
                or not check_password(old_password, row.password_hash)
            ):
                raise InvalidCredentialsError("Ancien mot de passe incorrect.")

            password_hash = hash_password(new_password)

        updated = self._user_dao.update_user(
            user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            # on ne touche PAS au status ici (pas demandé + sécurité)
            status=None,
        )

        if updated is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")
        return updated

    @staticmethod
    def _generate_password(*, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @log
    def admin_update_user(
        self,
        user_id: int,
        *,
        username: str | None = None,
        email: str | None = None,
        status: str | None = None,
        reset_password: bool = False,
    ) -> tuple[User, str | None]:
        row = self._user_dao.get_user_row_by_id(user_id)
        if row is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

        if email is not None:
            existing = self._user_dao.get_user_row_by_email(email)
            if existing is not None and existing.user_id != user_id:
                raise UserAlreadyExistsError("Email déjà utilisé.")

        if username is not None:
            existing = self._user_dao.get_user_row_by_username(username)
            if existing is not None and existing.user_id != user_id:
                raise UserAlreadyExistsError("Nom d’utilisateur déjà utilisé.")

        generated_password: str | None = None
        password_hash: str | None = None
        if reset_password:
            generated_password = self._generate_password(length=12)
            password_hash = hash_password(generated_password)

        updated = self._user_dao.update_user(
            user_id,
            username=username,
            email=email,
            status=status,
            password_hash=password_hash,
        )
        if updated is None:
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable.")

        return updated, generated_password
