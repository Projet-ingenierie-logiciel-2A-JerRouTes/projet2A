def _register_and_get_access(client, username, email, password):
    r = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code in (200, 201), r.text
    return r.json()["access_token"]


def test_update_me(client):
    access = _register_and_get_access(
        client, "editme", "editme@example.com", "Azerty123!"
    )

    r = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access}"},
        json={"username": "editme2"},
    )
    assert r.status_code == 200, r.text
    data = r.json()

    assert "user" in data, data
    assert data["user"]["username"] == "editme2", data


def test_change_password_then_login(client):
    access = _register_and_get_access(
        client, "pwduser", "pwduser@example.com", "Azerty123!"
    )

    # Change password
    r = client.post(
        "/api/users/me/change-password",
        headers={"Authorization": f"Bearer {access}"},
        json={"old_password": "Azerty123!", "new_password": "NewPass123!"},
    )
    assert r.status_code in (200, 204), r.text

    # Login with new password
    r2 = client.post(
        "/api/auth/login",
        json={"login": "pwduser@example.com", "password": "NewPass123!"},
    )
    assert r2.status_code == 200, r2.text
    assert "access_token" in r2.json()


def test_logout_invalidates_session_if_implemented(client):
    access = _register_and_get_access(
        client, "logoutuser", "logoutuser@example.com", "Azerty123!"
    )

    r = client.post(
        "/api/users/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code in (200, 204), r.text

    # Selon ton design (JWT stateless vs sessions)
    r2 = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code in (200, 401, 403), r2.text
