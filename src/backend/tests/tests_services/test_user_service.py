from __future__ import annotations

import pytest

from business_objects.user import GenericUser
from services.user_service import (
    AuthResult,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
    UserService,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def make_user_row(
    user_id=1,
    username="alice",
    email="alice@example.com",
    password_hash="$2b$12$hash",
    status="user",
    created_at="2026-01-01 10:00:00",
):
    # On évite d'importer UserRow si c'est contraignant : mocker accepte un objet
    # avec les attributs attendus (duck typing).
    class _Row:
        def __init__(self):
            self.user_id = user_id
            self.username = username
            self.email = email
            self.password_hash = password_hash
            self.status = status
            self.created_at = created_at

    return _Row()


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def mock_dao(mocker):
    return mocker.Mock(name="UserDAO")


@pytest.fixture
def service(mock_dao):
    return UserService(user_dao=mock_dao)


# ---------------------------------------------------------------------
# Tests : get_user
# ---------------------------------------------------------------------


def test_get_user_ok(service, mock_dao):
    mock_dao.get_user_by_id.return_value = GenericUser(1, "alice", "hash")

    user = service.get_user(1)

    assert user.id_user == 1
    assert user.pseudo == "alice"
    mock_dao.get_user_by_id.assert_called_once_with(1)


def test_get_user_not_found(service, mock_dao):
    mock_dao.get_user_by_id.return_value = None

    with pytest.raises(UserNotFoundError):
        service.get_user(999)


# ---------------------------------------------------------------------
# Tests : get_user_row_by_email
# ---------------------------------------------------------------------


def test_get_user_row_by_email_ok(service, mock_dao):
    row = make_user_row(user_id=2, email="bob@example.com", username="bob")
    mock_dao.get_user_row_by_email.return_value = row

    out = service.get_user_row_by_email("bob@example.com")

    assert out.user_id == 2
    assert out.email == "bob@example.com"
    mock_dao.get_user_row_by_email.assert_called_once_with("bob@example.com")


def test_get_user_row_by_email_not_found(service, mock_dao):
    mock_dao.get_user_row_by_email.return_value = None

    with pytest.raises(UserNotFoundError):
        service.get_user_row_by_email("nope@example.com")


# ---------------------------------------------------------------------
# Tests : register
# ---------------------------------------------------------------------


def test_register_ok(service, mock_dao, mocker):
    # email/username libres
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = None

    # mock hash_password
    mocker.patch("services.user_service.hash_password", return_value="HASHED")

    created_user = GenericUser(10, "alice", "HASHED")
    mock_dao.create_user.return_value = created_user

    user = service.register(
        username="alice", email="alice@example.com", password="Azerty123!"
    )

    assert user == created_user
    mock_dao.create_user.assert_called_once_with(
        username="alice",
        email="alice@example.com",
        password_hash="HASHED",
        status="user",
    )


def test_register_email_already_used(service, mock_dao, mocker):
    mock_dao.get_user_row_by_email.return_value = make_user_row(
        email="alice@example.com"
    )
    mock_dao.get_user_row_by_username.return_value = None

    mock_hash = mocker.patch("services.user_service.hash_password")

    with pytest.raises(UserEmailAlreadyExistsError):
        service.register(username="alice", email="alice@example.com", password="x")

    mock_hash.assert_not_called()
    mock_dao.create_user.assert_not_called()


def test_register_username_already_used(service, mock_dao, mocker):
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = make_user_row(username="alice")

    mock_hash = mocker.patch("services.user_service.hash_password")

    with pytest.raises(UserAlreadyExistsError):
        service.register(username="alice", email="alice@example.com", password="x")

    mock_hash.assert_not_called()
    mock_dao.create_user.assert_not_called()


# ---------------------------------------------------------------------
# Tests : authenticate (email OU username)
# ---------------------------------------------------------------------


def test_authenticate_with_email_ok(service, mock_dao, mocker):
    row = make_user_row(
        user_id=3, email="alice@example.com", username="alice", password_hash="HASH"
    )
    mock_dao.get_user_row_by_email.return_value = row
    mock_dao.get_user_row_by_username.return_value = None  # pas utilisé
    mock_dao.get_user_by_id.return_value = GenericUser(3, "alice", "HASH")

    mocker.patch("services.user_service.check_password", return_value=True)

    res = service.authenticate(login="alice@example.com", password="Azerty123!")

    assert isinstance(res, AuthResult)
    assert res.user.id_user == 3
    assert res.user.pseudo == "alice"

    mock_dao.get_user_row_by_email.assert_called_once_with("alice@example.com")
    mock_dao.get_user_row_by_username.assert_not_called()
    mock_dao.get_user_by_id.assert_called_once_with(3)


def test_authenticate_with_username_ok(service, mock_dao, mocker):
    mock_dao.get_user_row_by_email.return_value = None
    row = make_user_row(
        user_id=4, email="bob@example.com", username="bob", password_hash="HASH"
    )
    mock_dao.get_user_row_by_username.return_value = row
    mock_dao.get_user_by_id.return_value = GenericUser(4, "bob", "HASH")

    mocker.patch("services.user_service.check_password", return_value=True)

    res = service.authenticate(login="bob", password="Azerty123!")

    assert res.user.id_user == 4
    assert res.user.pseudo == "bob"
    mock_dao.get_user_row_by_email.assert_called_once_with("bob")
    mock_dao.get_user_row_by_username.assert_called_once_with("bob")


def test_authenticate_user_not_found(service, mock_dao, mocker):
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = None

    mocker.patch("services.user_service.check_password", return_value=True)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(login="nope", password="x")

    mock_dao.get_user_by_id.assert_not_called()


def test_authenticate_bad_password(service, mock_dao, mocker):
    row = make_user_row(
        user_id=5, email="alice@example.com", username="alice", password_hash="HASH"
    )
    mock_dao.get_user_row_by_email.return_value = row
    mock_dao.get_user_row_by_username.return_value = None

    mocker.patch("services.user_service.check_password", return_value=False)

    with pytest.raises(InvalidCredentialsError):
        service.authenticate(login="alice@example.com", password="wrong")

    mock_dao.get_user_by_id.assert_not_called()


def test_authenticate_inconsistent_db_user_missing(service, mock_dao, mocker):
    row = make_user_row(
        user_id=6, email="alice@example.com", username="alice", password_hash="HASH"
    )
    mock_dao.get_user_row_by_email.return_value = row
    mock_dao.get_user_row_by_username.return_value = None
    mock_dao.get_user_by_id.return_value = None

    mocker.patch("services.user_service.check_password", return_value=True)

    with pytest.raises(UserNotFoundError):
        service.authenticate(login="alice@example.com", password="Azerty123!")


# ---------------------------------------------------------------------
# Tests : update_profile
# ---------------------------------------------------------------------


def test_update_profile_ok(service, mock_dao):
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = None

    updated_user = GenericUser(1, "alice2", "hash")
    mock_dao.update_user.return_value = updated_user

    out = service.update_profile(1, username="alice2", email="a2@example.com")

    assert out == updated_user
    mock_dao.update_user.assert_called_once_with(
        1, username="alice2", email="a2@example.com", status=None
    )


def test_update_profile_email_collision(service, mock_dao):
    # email appartient à quelqu'un d'autre (user_id différent)
    existing = make_user_row(user_id=99, email="taken@example.com", username="taken")
    mock_dao.get_user_row_by_email.return_value = existing
    mock_dao.get_user_row_by_username.return_value = None

    with pytest.raises(UserAlreadyExistsError):
        service.update_profile(1, email="taken@example.com")

    mock_dao.update_user.assert_not_called()


def test_update_profile_username_collision(service, mock_dao):
    existing = make_user_row(user_id=99, username="taken", email="taken@example.com")
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = existing

    with pytest.raises(UserAlreadyExistsError):
        service.update_profile(1, username="taken")

    mock_dao.update_user.assert_not_called()


def test_update_profile_user_not_found(service, mock_dao):
    mock_dao.get_user_row_by_email.return_value = None
    mock_dao.get_user_row_by_username.return_value = None
    mock_dao.update_user.return_value = None

    with pytest.raises(UserNotFoundError):
        service.update_profile(999, username="x")


# ---------------------------------------------------------------------
# Tests : change_password
# ---------------------------------------------------------------------


def test_change_password_ok(service, mock_dao, mocker):
    row = make_user_row(user_id=1, password_hash="OLD_HASH")
    mock_dao.get_user_row_by_id.return_value = row

    mocker.patch("services.user_service.check_password", return_value=True)
    mocker.patch("services.user_service.hash_password", return_value="NEW_HASH")

    mock_dao.update_user.return_value = GenericUser(1, "alice", "NEW_HASH")

    service.change_password(user_id=1, old_password="old", new_password="new")

    mock_dao.update_user.assert_called_once_with(1, password_hash="NEW_HASH")


def test_change_password_wrong_old_password(service, mock_dao, mocker):
    row = make_user_row(user_id=1, password_hash="OLD_HASH")
    mock_dao.get_user_row_by_id.return_value = row

    mocker.patch("services.user_service.check_password", return_value=False)
    mock_hash = mocker.patch("services.user_service.hash_password")

    with pytest.raises(InvalidCredentialsError):
        service.change_password(user_id=1, old_password="wrong", new_password="new")

    mock_hash.assert_not_called()
    mock_dao.update_user.assert_not_called()


def test_change_password_user_not_found(service, mock_dao, mocker):
    mock_dao.get_user_row_by_id.return_value = None
    mocker.patch("services.user_service.check_password", return_value=True)

    with pytest.raises(UserNotFoundError):
        service.change_password(user_id=999, old_password="x", new_password="y")

    mock_dao.update_user.assert_not_called()


def test_change_password_update_returns_none(service, mock_dao, mocker):
    row = make_user_row(user_id=1, password_hash="OLD_HASH")
    mock_dao.get_user_row_by_id.return_value = row

    mocker.patch("services.user_service.check_password", return_value=True)
    mocker.patch("services.user_service.hash_password", return_value="NEW_HASH")

    mock_dao.update_user.return_value = None

    with pytest.raises(UserNotFoundError):
        service.change_password(user_id=1, old_password="old", new_password="new")


# ---------------------------------------------------------------------
# Tests : delete_user
# ---------------------------------------------------------------------


def test_delete_user_ok(service, mock_dao):
    mock_dao.delete_user.return_value = True

    service.delete_user(1)

    mock_dao.delete_user.assert_called_once_with(1)


def test_delete_user_not_found(service, mock_dao):
    mock_dao.delete_user.return_value = False

    with pytest.raises(UserNotFoundError):
        service.delete_user(999)
