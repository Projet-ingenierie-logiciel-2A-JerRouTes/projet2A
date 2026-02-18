from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dao.db_connection import DBConnection
from utils.log_decorator import log


@dataclass(frozen=True, slots=True)
class UserSession:
    session_id: int
    fk_user_id: int
    refresh_token_hash: str
    created_at: Any
    expires_at: Any
    revoked_at: Any
    last_seen_at: Any
    ip: str | None
    user_agent: str | None


class SessionDAO:
    """DAO pour la table `user_session`."""

    @staticmethod
    def _row_to_session(row: dict[str, Any]) -> UserSession:
        return UserSession(
            session_id=row["session_id"],
            fk_user_id=row["fk_user_id"],
            refresh_token_hash=row["refresh_token_hash"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            revoked_at=row["revoked_at"],
            last_seen_at=row["last_seen_at"],
            ip=row.get("ip"),
            user_agent=row.get("user_agent"),
        )

    # ------------------------------------------------------------------
    # Create / Read
    # ------------------------------------------------------------------

    @log
    def create_session(
        self,
        *,
        fk_user_id: int,
        refresh_token_hash: str,
        expires_at: datetime,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> UserSession:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_session
                        (fk_user_id, refresh_token_hash, expires_at, ip, user_agent)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING session_id
                    """,
                    (fk_user_id, refresh_token_hash, expires_at, ip, user_agent),
                )
                session_id = int(cur.fetchone()["session_id"])

                cur.execute(
                    """
                    SELECT session_id, fk_user_id, refresh_token_hash,
                           created_at, expires_at, revoked_at, last_seen_at, ip, user_agent
                    FROM user_session
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cur.fetchone()

            conn.commit()
            if not row:
                raise RuntimeError("Insertion session échouée (row=None).")
            return self._row_to_session(row)

        except Exception:
            conn.rollback()
            raise

    @log
    def get_session(self, session_id: int) -> UserSession | None:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT session_id, fk_user_id, refresh_token_hash,
                       created_at, expires_at, revoked_at, last_seen_at, ip, user_agent
                FROM user_session
                WHERE session_id = %s
                """,
                (session_id,),
            )
            row = cur.fetchone()
            return self._row_to_session(row) if row else None

    # ------------------------------------------------------------------
    # Update / Maintenance
    # ------------------------------------------------------------------

    @log
    def touch_session(self, session_id: int) -> bool:
        """Met à jour last_seen_at à maintenant."""
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_session
                    SET last_seen_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s AND revoked_at IS NULL
                    """,
                    (session_id,),
                )
                updated = cur.rowcount > 0

            conn.commit()
            return updated

        except Exception:
            conn.rollback()
            raise

    @log
    def rotate_refresh_token(
        self,
        *,
        session_id: int,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> UserSession | None:
        """
        Remplace le refresh_token_hash + expires_at (rotation).
        Ne modifie rien si la session est déjà révoquée.
        """
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_session
                    SET refresh_token_hash = %s,
                        expires_at = %s,
                        last_seen_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                      AND revoked_at IS NULL
                    """,
                    (refresh_token_hash, expires_at, session_id),
                )

                cur.execute(
                    """
                    SELECT session_id, fk_user_id, refresh_token_hash,
                           created_at, expires_at, revoked_at, last_seen_at, ip, user_agent
                    FROM user_session
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cur.fetchone()

            conn.commit()
            return self._row_to_session(row) if row else None

        except Exception:
            conn.rollback()
            raise

    @log
    def revoke_session(self, session_id: int) -> bool:
        """Révoque une session (logout)."""
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_session
                    SET revoked_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s AND revoked_at IS NULL
                    """,
                    (session_id,),
                )
                updated = cur.rowcount > 0

            conn.commit()
            return updated

        except Exception:
            conn.rollback()
            raise

    @log
    def revoke_all_user_sessions(self, fk_user_id: int) -> int:
        """Révoque toutes les sessions actives d'un user. Retourne le nombre révoqué."""
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_session
                    SET revoked_at = CURRENT_TIMESTAMP
                    WHERE fk_user_id = %s AND revoked_at IS NULL
                    """,
                    (fk_user_id,),
                )
                count = cur.rowcount

            conn.commit()
            return count

        except Exception:
            conn.rollback()
            raise

    # ------------------------------------------------------------------
    # (Optionnel) Helpers utiles
    # ------------------------------------------------------------------

    @log
    def find_active_session_by_hash(
        self, refresh_token_hash: str
    ) -> UserSession | None:
        """
        Trouve une session active via le hash.
        Pratique pour le refresh si tu ne veux pas passer session_id côté client.
        """
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT session_id, fk_user_id, refresh_token_hash,
                       created_at, expires_at, revoked_at, last_seen_at, ip, user_agent
                FROM user_session
                WHERE refresh_token_hash = %s
                  AND revoked_at IS NULL
                """,
                (refresh_token_hash,),
            )
            row = cur.fetchone()
            return self._row_to_session(row) if row else None
