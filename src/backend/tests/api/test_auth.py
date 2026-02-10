def test_register_then_me(client):
    r = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Azerty123!",
        },
    )
    assert r.status_code in (200, 201), r.text

    access = r.json()["access_token"]

    r2 = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200, r2.text
    me = r2.json()

    assert "user" in me, me
    assert me["user"]["username"] == "testuser", me
    assert me["user"]["email"] == "testuser@example.com", me


def test_register_duplicate_email(client):
    payload = {
        "username": "u11",  # >= 3 caractères (sinon 422)
        "email": "dup@example.com",
        "password": "Azerty123!",
    }

    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code in (200, 201), r1.text

    # Même email, username différent
    r2 = client.post(
        "/api/auth/register",
        json={**payload, "username": "u22"},
    )

    # Selon implémentation : 400 ou 409
    assert r2.status_code in (400, 409), r2.text


def test_login_wrong_password(client):
    # Create user
    client.post(
        "/api/auth/register",
        json={
            "username": "userbadpwd",
            "email": "badpwd@example.com",
            "password": "Azerty123!",
        },
    )

    # Wrong password
    r = client.post(
        "/api/auth/login",
        json={"login": "badpwd@example.com", "password": "WRONGPASS"},
    )
    assert r.status_code in (400, 401), r.text


def test_me_requires_token(client):
    r = client.get("/api/users/me")
    assert r.status_code in (401, 403), r.text
