import pytest

from src.backend.business_objects.user import Admin, GenericUser


@pytest.fixture(autouse=True)
def reset_users():
    GenericUser.users.clear()


def test_create_user():
    # Ajout de l'ID 1
    user = GenericUser.create_user(1, "alice", "1234")
    assert user.pseudo == "alice"
    # On utilise check_password au lieu de l'accès direct
    assert user.check_password("1234") is True
    assert user in GenericUser.users
    assert user.display_role() == "Utilisateur Générique"


def test_delete_user():
    user = GenericUser.create_user(2, "bob", "abcd")
    GenericUser.delete_user(user)
    assert user not in GenericUser.users


def test_change_password_success():
    # Correction : ID + utilisation de _password pour le assert final
    user = GenericUser(3, "charlie", "oldpass")
    result = user.change_password("oldpass", "newpass")
    assert result is True
    assert user.check_password("newpass") is True


def test_change_password_failure():
    user = GenericUser(4, "david", "oldpass")
    result = user.change_password("wrongpass", "newpass")
    assert result is False
    assert user.check_password("oldpass") is True


def test_admin_role():
    admin = Admin(5, "root", "admin123")
    assert admin.display_role() == "Administrateur"


def test_admin_change_password():
    admin = Admin(6, "root", "admin123")
    # Dans ta classe Admin, tu as un setter @password.setter
    admin.password = "supersecret1"  # Attention à la validation (min 6 car.)
    assert admin.check_password("supersecret1") is True
