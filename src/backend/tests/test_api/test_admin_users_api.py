def _register(client, username: str, email: str, password: str = "Azerty123!"):
    r = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()


def _login_and_get_access(client, login: str, password: str):
    r = client.post(
        "/api/auth/login",
        json={"login": login, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _get_user_id_by_email(client, access: str, email: str) -> int:
    r = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text

    users = r.json()
    for u in users:
        if u.get("email") == email:
            return int(u["user_id"])

    raise AssertionError(f"User with email={email} not found in /api/users/")


def test_admin_can_change_status_and_reset_password(client):
    # Admin seedé dans pop_db_test.sql (si c'est bien le cas chez toi)
    admin_access = _login_and_get_access(client, "admin@example.com", "mdpAdmin123")

    # Create a normal user
    _register(client, "toedit", "toedit@example.com", "Azerty123!")
    target_id = _get_user_id_by_email(client, admin_access, "toedit@example.com")

    # Admin updates status + resets password
    r = client.patch(
        f"/api/users/{target_id}",
        headers={"Authorization": f"Bearer {admin_access}"},
        json={"status": "admin", "reset_password": True},
    )
    assert r.status_code == 200, r.text
    data = r.json()

    assert "user" in data, data
    assert data["user"]["user_id"] == target_id
    assert data["user"]["status"] == "admin"

    # reset_password=true -> backend returns generated_password
    assert data.get("generated_password"), data
    new_pwd = data["generated_password"]

    # The generated password should work for login
    r2 = client.post(
        "/api/auth/login",
        json={"login": "toedit@example.com", "password": new_pwd},
    )
    assert r2.status_code == 200, r2.text


def test_non_admin_cannot_update_other_user_as_admin(client):
    # Create two users
    reg1 = _register(client, "u1a", "u1a@example.com")
    _register(client, "u1b", "u1b@example.com")

    access_user1 = reg1["access_token"]

    # Find user2 id using an admin token (simple & fiable)
    admin_access = _login_and_get_access(client, "admin@example.com", "mdpAdmin123")
    target_id = _get_user_id_by_email(client, admin_access, "u1b@example.com")

    # Non-admin tries admin patch -> forbidden
    r = client.patch(
        f"/api/users/{target_id}",
        headers={"Authorization": f"Bearer {access_user1}"},
        json={"status": "admin"},
    )
    assert r.status_code == 403, r.text


def test_admin_update_conflict_email_returns_409(client):
    admin_access = _login_and_get_access(client, "admin@example.com", "mdpAdmin123")

    _register(client, "conflict1", "conflict1@example.com")
    _register(client, "conflict2", "conflict2@example.com")

    id1 = _get_user_id_by_email(client, admin_access, "conflict1@example.com")

    # Try to set email to an existing email
    r = client.patch(
        f"/api/users/{id1}",
        headers={"Authorization": f"Bearer {admin_access}"},
        json={"email": "conflict2@example.com"},
    )
    assert r.status_code == 409, r.text
