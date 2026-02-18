from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from business_objects.user import Admin, GenericUser, User
from dao.db_connection import DBConnection
from utils.log_decorator import log


@dataclass(frozen=True, slots=True)
class UserRow:
    """Représentation typée d'une ligne de la table `users`."""

    user_id: int
    username: str
    email: str
    password_hash: str
    status: str
    created_at: Any


class UserDAO:
    """DAO pour la table `users`."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_bo(row: UserRow) -> User:
        if row.status == "admin":
            return Admin(
                row.user_id,
                row.username,
                row.password_hash,
                email=row.email,
                status=row.status,
            )
        return GenericUser(
            row.user_id,
            row.username,
            row.password_hash,
            email=row.email,
            status=row.status,
        )

    @staticmethod
    def _fetch_one_by_id(cur, user_id: int) -> UserRow | None:
        cur.execute(
            """
            SELECT user_id, username, email, password_hash, status, created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )
        row = cur.fetchone()
        return UserRow(**row) if row else None

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @log
    def create_user(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
        status: str = "user",
    ) -> User:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (username, email, password_hash, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING user_id
                    """,
                    (username, email, password_hash, status),
                )
                user_id = int(cur.fetchone()["user_id"])
                row = self._fetch_one_by_id(cur, user_id)

                if row is None:
                    raise RuntimeError("Insertion utilisateur échouée (row=None).")

            conn.commit()
            return self._row_to_bo(row)

        except Exception:
            conn.rollback()
            raise

    @log
    def get_user_by_id(self, user_id: int) -> User | None:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            row = self._fetch_one_by_id(cur, user_id)
            return self._row_to_bo(row) if row else None

    @log
    def get_user_row_by_id(self, user_id: int) -> UserRow | None:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            return self._fetch_one_by_id(cur, user_id)

    @log
    def get_user_row_by_email(self, email: str) -> UserRow | None:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, username, email, password_hash, status, created_at
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            row = cur.fetchone()
            return UserRow(**row) if row else None

    @log
    def get_user_row_by_username(self, username: str) -> UserRow | None:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, username, email, password_hash, status, created_at
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            row = cur.fetchone()
            return UserRow(**row) if row else None

    @log
    def update_user(
        self,
        user_id: int,
        *,
        username: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
        status: str | None = None,
    ) -> User | None:
        fields: list[str] = []
        params: list[Any] = []

        if username is not None:
            fields.append("username = %s")
            params.append(username)
        if email is not None:
            fields.append("email = %s")
            params.append(email)
        if password_hash is not None:
            fields.append("password_hash = %s")
            params.append(password_hash)
        if status is not None:
            fields.append("status = %s")
            params.append(status)

        if not fields:
            return self.get_user_by_id(user_id)

        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE users
                    SET {", ".join(fields)}
                    WHERE user_id = %s
                    """,
                    (*params, user_id),
                )

                row = self._fetch_one_by_id(cur, user_id)

            conn.commit()
            return self._row_to_bo(row) if row else None

        except Exception:
            conn.rollback()
            raise

    @log
    def delete_user(self, user_id: int) -> bool:
        conn = DBConnection().connection
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                deleted = cur.rowcount > 0

            conn.commit()
            return deleted

        except Exception:
            conn.rollback()
            raise

    @log
    def get_all_user_rows(self, limit: int | None = None) -> list[UserRow]:
        conn = DBConnection().connection
        with conn.cursor() as cur:
            query = """
                SELECT user_id, username, email, password_hash, status, created_at
                FROM users
                ORDER BY user_id
            """
            params: tuple[Any, ...] = ()

            if limit is not None:
                query += " LIMIT %s"
                params = (limit,)

            cur.execute(query, params)
            rows = cur.fetchall()

            return [UserRow(**row) for row in rows]

    @log
    def get_all_users(self, limit: int | None = None) -> list[User]:
        user_rows = self.get_all_user_rows(limit=limit)
        return [self._row_to_bo(row) for row in user_rows]
