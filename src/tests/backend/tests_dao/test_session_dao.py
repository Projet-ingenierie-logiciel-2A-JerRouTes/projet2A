from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from src.backend.dao.session_dao import SessionDAO, UserSession


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def dao() -> SessionDAO:
    return SessionDAO()


@pytest.fixture
def mock_db(mocker):
    """
    Mock complet de DBConnection -> connection -> cursor.

    Compatible avec:
    - with conn.cursor() as cur:
    """
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    # Patch DBConnection dans le module utilisé par la DAO
    mocker.patch("src.backend.dao.session_dao.DBConnection", return_value=db)

    return conn, cur


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def session_row(
    session_id=1,
    fk_user_id=10,
    refresh_token_hash="a" * 64,
    created_at="2026-01-01 10:00:00",
    expires_at="2026-02-01 10:00:00",
    revoked_at=None,
    last_seen_at=None,
    ip="127.0.0.1",
    user_agent="pytest",
):
    return {
        "session_id": session_id,
        "fk_user_id": fk_user_id,
        "refresh_token_hash": refresh_token_hash,
        "created_at": created_at,
        "expires_at": expires_at,
        "revoked_at": revoked_at,
        "last_seen_at": last_seen_at,
        "ip": ip,
        "user_agent": user_agent,
    }


def executed_sql_list(cur) -> list[str]:
    return [str(c[0][0]) for c in cur.execute.call_args_list]


# ---------------------------------------------------------------------
# Tests : create_session
# ---------------------------------------------------------------------


def test_create_session_success(dao, mock_db):
    conn, cur = mock_db

    exp = datetime.now(UTC) + timedelta(days=7)

    # 1) INSERT ... RETURNING session_id
    # 2) SELECT ... WHERE session_id = %s
    cur.fetchone.side_effect = [
        {"session_id": 123},
        session_row(session_id=123, fk_user_id=10),
    ]

    s = dao.create_session(
        fk_user_id=10,
        refresh_token_hash="b" * 64,
        expires_at=exp,
        ip="127.0.0.1",
        user_agent="pytest",
    )

    assert isinstance(s, UserSession)
    assert s.session_id == 123
    assert s.fk_user_id == 10

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO user_session" in s for s in sqls)
    assert any("FROM user_session" in s for s in sqls)


def test_create_session_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.create_session(
            fk_user_id=10,
            refresh_token_hash="c" * 64,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : get_session
# ---------------------------------------------------------------------


def test_get_session_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = session_row(session_id=50, fk_user_id=9)

    s = dao.get_session(50)
    assert s is not None
    assert s.session_id == 50
    assert s.fk_user_id == 9

    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()


def test_get_session_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    s = dao.get_session(999)
    assert s is None


# ---------------------------------------------------------------------
# Tests : touch_session
# ---------------------------------------------------------------------


def test_touch_session_true_when_updated(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1

    ok = dao.touch_session(1)
    assert ok is True

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_touch_session_false_when_not_updated(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 0

    ok = dao.touch_session(1)
    assert ok is False

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_touch_session_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.touch_session(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : rotate_refresh_token
# ---------------------------------------------------------------------


def test_rotate_refresh_token_success_returns_session(dao, mock_db):
    conn, cur = mock_db

    exp = datetime.now(UTC) + timedelta(days=7)

    # rotate fait:
    # 1) UPDATE ...
    # 2) SELECT ...
    cur.fetchone.return_value = session_row(
        session_id=77, fk_user_id=10, refresh_token_hash="z" * 64
    )

    s = dao.rotate_refresh_token(
        session_id=77,
        refresh_token_hash="z" * 64,
        expires_at=exp,
    )

    assert s is not None
    assert s.session_id == 77
    assert s.refresh_token_hash == "z" * 64

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_rotate_refresh_token_returns_none_if_session_missing(dao, mock_db):
    conn, cur = mock_db

    exp = datetime.now(UTC) + timedelta(days=7)

    cur.fetchone.return_value = None  # SELECT after update returns nothing

    s = dao.rotate_refresh_token(
        session_id=999,
        refresh_token_hash="y" * 64,
        expires_at=exp,
    )

    assert s is None
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_rotate_refresh_token_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.rotate_refresh_token(
            session_id=1,
            refresh_token_hash="x" * 64,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : revoke_session
# ---------------------------------------------------------------------


def test_revoke_session_true_when_updated(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1

    ok = dao.revoke_session(1)
    assert ok is True

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_revoke_session_false_when_not_updated(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 0

    ok = dao.revoke_session(1)
    assert ok is False

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_revoke_session_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.revoke_session(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : revoke_all_user_sessions
# ---------------------------------------------------------------------


def test_revoke_all_user_sessions_returns_count(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 3

    count = dao.revoke_all_user_sessions(10)
    assert count == 3

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_revoke_all_user_sessions_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.revoke_all_user_sessions(10)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : find_active_session_by_hash (optionnel)
# ---------------------------------------------------------------------


def test_find_active_session_by_hash_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = session_row(session_id=12, fk_user_id=5)

    s = dao.find_active_session_by_hash("a" * 64)
    assert s is not None
    assert s.session_id == 12
    assert s.fk_user_id == 5


def test_find_active_session_by_hash_not_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = None

    s = dao.find_active_session_by_hash("b" * 64)
    assert s is None
