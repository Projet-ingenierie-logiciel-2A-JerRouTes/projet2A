from __future__ import annotations

import pytest

from src.backend.business_objects.user import Admin, GenericUser
from src.backend.dao.user_dao import UserDAO


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def dao() -> UserDAO:
    return UserDAO()


@pytest.fixture
def mock_db(mocker):
    """
    Mock complet de DBConnection -> connection -> cursor.

    Compatible avec:
    - with conn.cursor() as cur:
    - cur = conn.cursor(); cur.close()
    """
    cur = mocker.Mock(name="cursor")
    cur.__enter__ = mocker.Mock(return_value=cur)
    cur.__exit__ = mocker.Mock(return_value=None)

    conn = mocker.Mock(name="connection")
    conn.cursor = mocker.Mock(return_value=cur)

    db = mocker.Mock(name="DBConnectionInstance")
    db.connection = conn

    # Patch DBConnection dans le module utilisé par la DAO
    mocker.patch("src.backend.dao.user_dao.DBConnection", return_value=db)

    return conn, cur


# ---------------------------------------------------------------------
# Helpers données simulées
# ---------------------------------------------------------------------


def user_row(
    user_id=1,
    username="alice",
    email="alice@example.com",
    password_hash="$2b$12$hash",
    status="user",
    created_at="2026-01-01 12:00:00",
):
    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "status": status,
        "created_at": created_at,
    }


def executed_sql_list(cur) -> list[str]:
    return [str(c[0][0]) for c in cur.execute.call_args_list]


# ---------------------------------------------------------------------
# Tests : create_user
# ---------------------------------------------------------------------


def test_create_user_success_generic(dao, mock_db):
    conn, cur = mock_db

    # 1) INSERT ... RETURNING user_id
    # 2) SELECT ... WHERE user_id = %s
    cur.fetchone.side_effect = [
        {"user_id": 10},
        user_row(user_id=10, username="alice", status="user"),
    ]

    user = dao.create_user(
        username="alice",
        email="alice@example.com",
        password_hash="$2b$12$hash",
        status="user",
    )

    assert isinstance(user, GenericUser)
    assert user.id_user == 10
    assert user.pseudo == "alice"
    assert user.check_password("$2b$12$hash") is True  # hash stocké dans _password

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("INSERT INTO users" in s for s in sqls)
    assert any("SELECT user_id, username, email" in s for s in sqls)


def test_create_user_success_admin_mapping(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.side_effect = [
        {"user_id": 42},
        user_row(user_id=42, username="root", status="admin"),
    ]

    user = dao.create_user(
        username="root",
        email="root@example.com",
        password_hash="$2b$12$hash",
        status="admin",
    )

    assert isinstance(user, Admin)
    assert user.id_user == 42
    assert user.pseudo == "root"

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_create_user_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.create_user(
            username="alice",
            email="alice@example.com",
            password_hash="$2b$12$hash",
            status="user",
        )

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : get_user_by_id / get_user_row_by_*
# ---------------------------------------------------------------------


def test_get_user_by_id_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = user_row(user_id=5, username="alice", status="user")

    user = dao.get_user_by_id(5)

    assert isinstance(user, GenericUser)
    assert user.id_user == 5
    assert user.pseudo == "alice"
    conn.commit.assert_not_called()
    conn.rollback.assert_not_called()


def test_get_user_by_id_not_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = None

    user = dao.get_user_by_id(999)
    assert user is None


def test_get_user_row_by_email_found(dao, mock_db):
    conn, cur = mock_db

    cur.fetchone.return_value = user_row(user_id=7, username="alice")

    row = dao.get_user_row_by_email("alice@example.com")

    assert row is not None
    assert row.user_id == 7
    assert row.email == "alice@example.com"
    assert row.username == "alice"


def test_get_user_row_by_username_not_found(dao, mock_db):
    conn, cur = mock_db
    cur.fetchone.return_value = None

    row = dao.get_user_row_by_username("nobody")
    assert row is None


# ---------------------------------------------------------------------
# Tests : update_user
# ---------------------------------------------------------------------


def test_update_user_no_fields_returns_current(mocker, dao, mock_db):
    """
    Dans ton UserDAO, si aucun champ n'est fourni,
    update_user renvoie get_user_by_id(user_id).
    """
    conn, cur = mock_db

    fake_user = GenericUser(1, "alice", "hash")
    mocker.patch.object(dao, "get_user_by_id", return_value=fake_user)

    out = dao.update_user(1)

    assert out == fake_user
    cur.execute.assert_not_called()


def test_update_user_success(dao, mock_db):
    conn, cur = mock_db

    # Après l'UPDATE, le DAO refetch par id
    cur.fetchone.return_value = user_row(
        user_id=10, username="alice2", email="a2@ex.com"
    )

    user = dao.update_user(
        10,
        username="alice2",
        email="a2@ex.com",
    )

    assert user is not None
    assert user.id_user == 10
    assert user.pseudo == "alice2"

    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()

    sqls = executed_sql_list(cur)
    assert any("UPDATE users" in s for s in sqls)
    assert any("WHERE user_id = %s" in s for s in sqls)


def test_update_user_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    # erreur sur UPDATE
    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.update_user(1, username="alice2")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


# ---------------------------------------------------------------------
# Tests : delete_user
# ---------------------------------------------------------------------


def test_delete_user_true_if_row_deleted(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 1

    ok = dao.delete_user(1)

    assert ok is True
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_delete_user_false_if_no_row(dao, mock_db):
    conn, cur = mock_db

    cur.rowcount = 0

    ok = dao.delete_user(999)

    assert ok is False
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_delete_user_rollback_on_error(dao, mock_db):
    conn, cur = mock_db

    cur.execute.side_effect = RuntimeError("DB error")

    with pytest.raises(RuntimeError):
        dao.delete_user(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
