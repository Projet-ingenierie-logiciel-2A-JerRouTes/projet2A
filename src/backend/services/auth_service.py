from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from src.backend.dao.session_dao import SessionDAO
from src.backend.dao.user_dao import UserDAO
from src.backend.utils.jwt_utils import encode_jwt
from src.backend.utils.log_decorator import log
from src.backend.utils.securite import check_password


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------


class AuthServiceError(Exception):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class InvalidRefreshTokenError(AuthServiceError):
    pass


# ---------------------------------------------------------------------
# DTO
# ---------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    session_id: int


# ---------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------


class AuthService:
    def __init__(
        self,
        user_dao: UserDAO | None = None,
        session_dao: SessionDAO | None = None,
        *,
        jwt_secret: str = "CHANGE_ME",
        jwt_issuer: str = "projet2a",
        access_ttl_minutes: int = 15,
        refresh_ttl_days: int = 7,
    ) -> None:
        self._user_dao = user_dao or UserDAO()
        self._session_dao = session_dao or SessionDAO()

        self._jwt_secret = jwt_secret
        self._jwt_issuer = jwt_issuer
        self._access_ttl_minutes = access_ttl_minutes
        self._refresh_ttl_days = refresh_ttl_days

    # --------------------------------------------------------------
    # Utils
    # --------------------------------------------------------------

    @staticmethod
    def _hash_refresh(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _new_refresh_token() -> str:
        # token URL-safe, long, impossible à deviner
        return secrets.token_urlsafe(48)

    def _make_access_token(self, *, user_id: int, status: str, session_id: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "iss": self._jwt_issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._access_ttl_minutes)).timestamp()),
            "uid": user_id,
            "sid": session_id,
            "status": status,
        }
        return encode_jwt(payload, secret=self._jwt_secret)

    # --------------------------------------------------------------
    # Login
    # --------------------------------------------------------------

    @log
    def login(
        self,
        *,
        login: str,
        password: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPair:
        # 1) trouver le user (email ou username)
        row = self._user_dao.get_user_row_by_email(login)
        if row is None:
            row = self._user_dao.get_user_row_by_username(login)

        if row is None:
            raise InvalidCredentialsError("Identifiants invalides.")

        # 2) vérifier le mot de passe
        if not check_password(password, row.password_hash):
            raise InvalidCredentialsError("Identifiants invalides.")

        # 3) créer session + refresh token
        refresh = self._new_refresh_token()
        refresh_hash = self._hash_refresh(refresh)
        expires_at = datetime.now(UTC) + timedelta(days=self._refresh_ttl_days)

        session = self._session_dao.create_session(
            fk_user_id=row.user_id,
            refresh_token_hash=refresh_hash,
            expires_at=expires_at,
            ip=ip,
            user_agent=user_agent,
        )

        # 4) access token
        access = self._make_access_token(
            user_id=row.user_id,
            status=row.status,
            session_id=session.session_id,
        )

        return TokenPair(
            access_token=access, refresh_token=refresh, session_id=session.session_id
        )

    # --------------------------------------------------------------
    # Refresh
    # --------------------------------------------------------------

    @log
    def refresh(self, *, refresh_token: str) -> TokenPair:
        refresh_hash = self._hash_refresh(refresh_token)

        session = self._session_dao.find_active_session_by_hash(refresh_hash)
        if session is None:
            raise InvalidRefreshTokenError("Refresh token invalide.")

        # vérifier expiration (en Python côté service)
        now = datetime.now(UTC)
        # session.expires_at peut être timezone-naive selon ton driver.
        # On gère le cas simple : si naive, on compare en naive.
        exp = session.expires_at
        if exp is not None:
            if exp.tzinfo is None:
                if exp <= datetime.now():
                    raise InvalidRefreshTokenError("Session expirée.")
            else:
                if exp <= now:
                    raise InvalidRefreshTokenError("Session expirée.")

        # rotation
        new_refresh = self._new_refresh_token()
        new_refresh_hash = self._hash_refresh(new_refresh)
        new_expires_at = datetime.now(UTC) + timedelta(days=self._refresh_ttl_days)

        rotated = self._session_dao.rotate_refresh_token(
            session_id=session.session_id,
            refresh_token_hash=new_refresh_hash,
            expires_at=new_expires_at,
        )
        if rotated is None:
            raise InvalidRefreshTokenError("Session invalide ou révoquée.")

        # user info pour status (on relit le user)
        user_row = self._user_dao.get_user_row_by_id(session.fk_user_id)
        if user_row is None:
            raise InvalidRefreshTokenError("Utilisateur introuvable.")

        access = self._make_access_token(
            user_id=user_row.user_id,
            status=user_row.status,
            session_id=session.session_id,
        )

        return TokenPair(
            access_token=access,
            refresh_token=new_refresh,
            session_id=session.session_id,
        )

    # --------------------------------------------------------------
    # Logout
    # --------------------------------------------------------------

    @log
    def logout(self, *, session_id: int) -> bool:
        return self._session_dao.revoke_session(session_id)

    @log
    def logout_all(self, *, user_id: int) -> int:
        return self._session_dao.revoke_all_user_sessions(user_id)
