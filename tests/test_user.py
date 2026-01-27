import pytest

from src.business_objects.user import Admin, GenericUser


@pytest.fixture(autouse=True)
def reset_users():
    GenericUser.users.clear()


def test_create_user():
    user = GenericUser.create_user("alice", "1234")
    assert user.pseudo == "alice"
    assert user.password == "1234"
    assert user in GenericUser.users
    assert user.display_role() == "Generic User"


def test_delete_user():
    user = GenericUser.create_user("bob", "abcd")
    GenericUser.delete_user(user)
    assert user not in GenericUser.users


def test_change_password_success():
    user = GenericUser("charlie", "oldpass")
    result = user.change_password("oldpass", "newpass")
    assert result is True
    assert user.password == "newpass"


def test_change_password_failure():
    user = GenericUser("david", "oldpass")
    result = user.change_password("wrongpass", "newpass")
    assert result is False
    assert user.password == "oldpass"


def test_admin_role():
    admin = Admin("root", "admin123")
    assert admin.display_role() == "Admin"


def test_admin_change_password():
    admin = Admin("root", "admin123")
    admin.change_admin_password("supersecret")
    assert admin.password == "supersecret"
