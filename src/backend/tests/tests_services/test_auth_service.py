from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest
from src.backend.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    TokenPair,
)


# ---------------------------------------------------------------------
# Helpers : faux rows (duck typing)
# ---------------------------------------------------------------------


def make_user_row(
    user_id=1,
    username="alice",
    email="alice@example.com",
    password_hash="HASH",
    status="user",
    created_at="2026-01-01 10:00:00",
):
    class _Row:
        def __init__(self):
            self.user_id = user_id
            self.username = username
            self.email = email
            self.password_hash = password_hash
            self.status = status
            self.created_at = created_at

    return _Row()


@dataclass(frozen=True, slots=True)
class FakeSession:
    session_id: int
    fk_user_id: int
    refresh_token_hash: str
    created_at: object = None
    expires_at: object = None
    revoked_at: object = None
    last_seen_at: object = None
    ip: str | None = None
    user_agent: str | None = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def mock_user_dao(mocker):
    return mocker.Mock(name="UserDAO")


@pytest.fixture
def mock_session_dao(mocker):
    return mocker.Mock(name="SessionDAO")


@pytest.fixture
def service(mock_user_dao, mock_session_dao):
    # jwt_secret fixe pour tests
    return AuthService(
        user_dao=mock_user_dao,
        session_dao=mock_session_dao,
        jwt_secret="TEST_SECRET",
        jwt_issuer="projet2a",
        access_ttl_minutes=15,
        refresh_ttl_days=7,
    )


# ---------------------------------------------------------------------
# Tests : login
# ---------------------------------------------------------------------


def test_login_ok_with_email(service, mock_user_dao, mock_session_dao, mocker):
    # Arrange
    row = make_user_row(
        user_id=10, email="alice@example.com", username="alice", status="user"
    )
    mock_user_dao.get_user_row_by_email.return_value = row
    mock_user_dao.get_user_row_by_username.return_value = None

    mocker.patch("src.backend.services.auth_service.check_password", return_value=True)

    # Refresh token déterministe
    mocker.patch.object(service, "_new_refresh_token", return_value="REFRESH_1")

    # Session créée en base
    mock_session_dao.create_session.return_value = FakeSession(
        session_id=123,
        fk_user_id=10,
        refresh_token_hash=service._hash_refresh("REFRESH_1"),
    )

    # JWT déterministe
    mocker.patch(
        "src.backend.services.auth_service.encode_jwt", return_value="ACCESS_TOKEN"
    )

    # Act
    tokens = service.login(
        login="alice@example.com", password="pwd", ip="1.2.3.4", user_agent="pytest"
    )

    # Assert
    assert isinstance(tokens, TokenPair)
    assert tokens.access_token == "ACCESS_TOKEN"
    assert tokens.refresh_token == "REFRESH_1"
    assert tokens.session_id == 123

    mock_user_dao.get_user_row_by_email.assert_called_once_with("alice@example.com")
    mock_user_dao.get_user_row_by_username.assert_not_called()

    mock_session_dao.create_session.assert_called_once()
    kwargs = mock_session_dao.create_session.call_args.kwargs
    assert kwargs["fk_user_id"] == 10
    assert kwargs["refresh_token_hash"] == service._hash_refresh("REFRESH_1")
    assert kwargs["ip"] == "1.2.3.4"
    assert kwargs["user_agent"] == "pytest"


def test_login_ok_with_username(service, mock_user_dao, mock_session_dao, mocker):
    # Arrange
    mock_user_dao.get_user_row_by_email.return_value = None
    row = make_user_row(
        user_id=11, email="bob@example.com", username="bob", status="admin"
    )
    mock_user_dao.get_user_row_by_username.return_value = row

    mocker.patch("src.backend.services.auth_service.check_password", return_value=True)
    mocker.patch.object(service, "_new_refresh_token", return_value="REFRESH_2")
    mock_session_dao.create_session.return_value = FakeSession(
        session_id=200,
        fk_user_id=11,
        refresh_token_hash=service._hash_refresh("REFRESH_2"),
    )
    mocker.patch(
        "src.backend.services.auth_service.encode_jwt", return_value="ACCESS_TOKEN_2"
    )

    # Act
    tokens = service.login(login="bob", password="pwd")

    # Assert
    assert tokens.access_token == "ACCESS_TOKEN_2"
    assert tokens.refresh_token == "REFRESH_2"
    assert tokens.session_id == 200

    mock_user_dao.get_user_row_by_email.assert_called_once_with("bob")
    mock_user_dao.get_user_row_by_username.assert_called_once_with("bob")


def test_login_invalid_credentials_user_not_found(service, mock_user_dao):
    mock_user_dao.get_user_row_by_email.return_value = None
    mock_user_dao.get_user_row_by_username.return_value = None

    with pytest.raises(InvalidCredentialsError):
        service.login(login="nope", password="pwd")


def test_login_invalid_credentials_bad_password(service, mock_user_dao, mocker):
    row = make_user_row(user_id=10)
    mock_user_dao.get_user_row_by_email.return_value = row
    mock_user_dao.get_user_row_by_username.return_value = None

    mocker.patch("src.backend.services.auth_service.check_password", return_value=False)

    with pytest.raises(InvalidCredentialsError):
        service.login(login="alice@example.com", password="wrong")


# ---------------------------------------------------------------------
# Tests : refresh
# ---------------------------------------------------------------------


def test_refresh_ok(service, mock_user_dao, mock_session_dao, mocker):
    # Arrange
    # session active trouvée par hash
    old_refresh = "REFRESH_OLD"
    old_hash = service._hash_refresh(old_refresh)

    # expires_at future timezone-aware
    exp = datetime.now(UTC) + timedelta(days=1)
    session = FakeSession(
        session_id=500,
        fk_user_id=10,
        refresh_token_hash=old_hash,
        expires_at=exp,
        revoked_at=None,
    )
    mock_session_dao.find_active_session_by_hash.return_value = session

    # rotation refresh
    mocker.patch.object(service, "_new_refresh_token", return_value="REFRESH_NEW")
    mock_session_dao.rotate_refresh_token.return_value = FakeSession(
        session_id=500,
        fk_user_id=10,
        refresh_token_hash=service._hash_refresh("REFRESH_NEW"),
    )

    # user pour status
    mock_user_dao.get_user_row_by_id.return_value = make_user_row(
        user_id=10, status="user"
    )

    # jwt déterministe
    mocker.patch(
        "src.backend.services.auth_service.encode_jwt", return_value="ACCESS_NEW"
    )

    # Act
    tokens = service.refresh(refresh_token=old_refresh)

    # Assert
    assert tokens.access_token == "ACCESS_NEW"
    assert tokens.refresh_token == "REFRESH_NEW"
    assert tokens.session_id == 500

    mock_session_dao.find_active_session_by_hash.assert_called_once_with(old_hash)
    mock_session_dao.rotate_refresh_token.assert_called_once()
    mock_user_dao.get_user_row_by_id.assert_called_once_with(10)


def test_refresh_invalid_when_not_found(service, mock_session_dao):
    mock_session_dao.find_active_session_by_hash.return_value = None

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh(refresh_token="NOPE")


def test_refresh_invalid_when_expired_timezone_aware(service, mock_session_dao):
    old_refresh = "REFRESH_OLD"
    expired = datetime.now(UTC) - timedelta(seconds=1)

    mock_session_dao.find_active_session_by_hash.return_value = FakeSession(
        session_id=1,
        fk_user_id=1,
        refresh_token_hash="x" * 64,
        expires_at=expired,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh(refresh_token=old_refresh)


def test_refresh_invalid_when_expired_timezone_naive(service, mock_session_dao):
    old_refresh = "REFRESH_OLD"
    expired_naive = datetime.now() - timedelta(seconds=1)

    mock_session_dao.find_active_session_by_hash.return_value = FakeSession(
        session_id=1,
        fk_user_id=1,
        refresh_token_hash="x" * 64,
        expires_at=expired_naive,
    )

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh(refresh_token=old_refresh)


def test_refresh_invalid_when_rotate_returns_none(
    service, mock_user_dao, mock_session_dao, mocker
):
    old_refresh = "REFRESH_OLD"
    exp = datetime.now(UTC) + timedelta(days=1)

    mock_session_dao.find_active_session_by_hash.return_value = FakeSession(
        session_id=2,
        fk_user_id=1,
        refresh_token_hash=service._hash_refresh(old_refresh),
        expires_at=exp,
    )

    mocker.patch.object(service, "_new_refresh_token", return_value="REFRESH_NEW")
    mock_session_dao.rotate_refresh_token.return_value = None

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh(refresh_token=old_refresh)

    mock_user_dao.get_user_row_by_id.assert_not_called()


def test_refresh_invalid_when_user_missing(
    service, mock_user_dao, mock_session_dao, mocker
):
    old_refresh = "REFRESH_OLD"
    exp = datetime.now(UTC) + timedelta(days=1)

    mock_session_dao.find_active_session_by_hash.return_value = FakeSession(
        session_id=3,
        fk_user_id=99,
        refresh_token_hash=service._hash_refresh(old_refresh),
        expires_at=exp,
    )

    mocker.patch.object(service, "_new_refresh_token", return_value="REFRESH_NEW")
    mock_session_dao.rotate_refresh_token.return_value = FakeSession(
        session_id=3,
        fk_user_id=99,
        refresh_token_hash=service._hash_refresh("REFRESH_NEW"),
    )

    mock_user_dao.get_user_row_by_id.return_value = None

    with pytest.raises(InvalidRefreshTokenError):
        service.refresh(refresh_token=old_refresh)


# ---------------------------------------------------------------------
# Tests : logout / logout_all
# ---------------------------------------------------------------------


def test_logout_calls_revoke_session(service, mock_session_dao):
    mock_session_dao.revoke_session.return_value = True

    ok = service.logout(session_id=10)

    assert ok is True
    mock_session_dao.revoke_session.assert_called_once_with(10)


def test_logout_all_calls_revoke_all(service, mock_session_dao):
    mock_session_dao.revoke_all_user_sessions.return_value = 3

    count = service.logout_all(user_id=10)

    assert count == 3
    mock_session_dao.revoke_all_user_sessions.assert_called_once_with(10)
