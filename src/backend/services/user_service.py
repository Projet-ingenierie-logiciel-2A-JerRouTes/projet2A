from __future__ import annotations

from dataclasses import dataclass

from src.backend.business_objects.user import User
from src.backend.dao.user_dao import UserDAO, UserRow
from src.backend.utils.log_decorator import log
from src.backend.utils.securite import check_password, hash_password


# ---------------------------------------------------------------------
# Exceptions "métier"
# ---------------------------------------------------------------------


class UserServiceError(Exception):
    """Base des erreurs du service user."""


class UserAlreadyExistsError(UserServiceError):
    """Email ou username déjà utilisé."""


class InvalidCredentialsError(UserServiceError):
    """Identifiants invalides."""


class UserNotFoundError(UserServiceError):
    """Utilisateur introuvable."""


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
            raise UserAlreadyExistsError("Email déjà utilisé.")
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
        """
        # 1) on essaie comme email
        row = self._user_dao.get_user_row_by_email(login)

        # 2) sinon comme username
        if row is None:
            row = self._user_dao.get_user_row_by_username(login)

        if row is None:
            raise InvalidCredentialsError("Identifiants invalides.")

        if not check_password(password, row.password_hash):
            raise InvalidCredentialsError("Identifiants invalides.")

        user = self._user_dao.get_user_by_id(row.user_id)
        if user is None:
            raise UserNotFoundError("Utilisateur introuvable.")

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
