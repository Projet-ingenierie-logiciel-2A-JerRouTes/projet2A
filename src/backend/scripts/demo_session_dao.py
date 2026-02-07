from datetime import UTC, datetime, timedelta
import hashlib

from src.backend.dao.session_dao import SessionDAO


# ---------------------------------------------------------------------
# Utils
# ---------------------------------------------------------------------


def hash_refresh_token(token: str) -> str:
    """Hash SHA-256 hex du refresh token (stockage en base)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------


def main():
    dao = SessionDAO()

    # ⚠️ IMPORTANT : ce user_id doit exister dans la table users
    fk_user_id = 1

    print("=== DEMO SessionDAO ===")

    # -----------------------------------------------------------------
    # 1) Création de session
    # -----------------------------------------------------------------
    refresh_token_1 = "refresh_token_demo_1"
    expires_at_1 = datetime.now(UTC) + timedelta(days=7)

    session = dao.create_session(
        fk_user_id=fk_user_id,
        refresh_token_hash=hash_refresh_token(refresh_token_1),
        expires_at=expires_at_1,
        ip="127.0.0.1",
        user_agent="demo-script",
    )

    print("\n[1] Session créée")
    print(session)

    # -----------------------------------------------------------------
    # 2) Lecture de la session
    # -----------------------------------------------------------------
    session_read = dao.get_session(session.session_id)

    print("\n[2] Session relue depuis la base")
    print(session_read)

    # -----------------------------------------------------------------
    # 3) Rotation du refresh token
    # -----------------------------------------------------------------
    refresh_token_2 = "refresh_token_demo_2"
    expires_at_2 = datetime.now(UTC) + timedelta(days=7)

    session_rotated = dao.rotate_refresh_token(
        session_id=session.session_id,
        refresh_token_hash=hash_refresh_token(refresh_token_2),
        expires_at=expires_at_2,
    )

    print("\n[3] Refresh token rotaté")
    print(session_rotated)

    # -----------------------------------------------------------------
    # 4) Touch session (last_seen_at)
    # -----------------------------------------------------------------
    touched = dao.touch_session(session.session_id)

    print("\n[4] Session touchée (last_seen_at mis à jour)")
    print("Succès :", touched)

    # -----------------------------------------------------------------
    # 5) Révocation de la session (logout)
    # -----------------------------------------------------------------
    revoked = dao.revoke_session(session.session_id)

    print("\n[5] Session révoquée")
    print("Succès :", revoked)

    # -----------------------------------------------------------------
    # 6) Tentative de rotation après révocation
    # -----------------------------------------------------------------
    session_after_revoke = dao.rotate_refresh_token(
        session_id=session.session_id,
        refresh_token_hash=hash_refresh_token("should_not_work"),
        expires_at=expires_at_2,
    )

    print("\n[6] Rotation après révocation (doit rester révoquée)")
    print(session_after_revoke)

    print("\n=== FIN DEMO ===")


if __name__ == "__main__":
    main()
