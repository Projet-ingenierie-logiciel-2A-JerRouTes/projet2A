import uuid


def _register_and_get_token(client) -> str:
    suffix = uuid.uuid4().hex[:8]
    r = client.post(
        "/api/auth/register",
        json={
            "username": f"u_{suffix}",
            "email": f"u_{suffix}@example.com",
            "password": "Azerty123!",
        },
    )
    assert r.status_code in (200, 201), r.text
    data = r.json()
    assert "access_token" in data, data
    return data["access_token"]


def test_get_recipe_requires_auth(client):
    r = client.get("/api/recipes/1")
    assert r.status_code in (401, 403), r.text


def test_get_recipe_ok(client):
    token = _register_and_get_token(client)

    r = client.get(
        "/api/recipes/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    data = r.json()

    # Champs principaux
    assert data["recipe_id"] == 1
    assert "creator_id" in data
    assert "status" in data
    assert "prep_time" in data
    assert "portions" in data

    # Relations
    assert isinstance(data["ingredients"], list)
    assert isinstance(data["tags"], list)

    # On sait qu'en DB de test, la recette 1 a des ingrédients
    assert len(data["ingredients"]) > 0
    assert all("ingredient_id" in x and "quantity" in x for x in data["ingredients"])


def test_get_recipe_404(client):
    token = _register_and_get_token(client)

    r = client.get(
        "/api/recipes/999999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text


def test_search_recipes_requires_auth(client):
    r = client.post(
        "/api/recipes/search",
        json={"ingredients": ["Egg", "Milk"]},
    )
    assert r.status_code in (401, 403), r.text


def test_search_recipes_ok(client):
    token = _register_and_get_token(client)

    r = client.post(
        "/api/recipes/search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ingredients": ["Egg", "Milk"],
            "limit": 10,
            "max_missing": 0,
            "strict_only": False,
            "dish_type": None,
            "ignore_pantry": True,
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)

    # Dans la DB de test :
    # - Pancakes (id=1) contient Egg + Milk
    recipe_ids = {x["recipe_id"] for x in data}
    assert 1 in recipe_ids, data


def test_search_recipes_with_dish_type_filter(client):
    token = _register_and_get_token(client)

    r = client.post(
        "/api/recipes/search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ingredients": ["Egg"],
            "limit": 10,
            "max_missing": 10,  # large tolérance
            "dish_type": "Dessert",  # tag en DB de test
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    recipe_ids = {x["recipe_id"] for x in data}

    # Dans la DB de test :
    # - Pancakes (id=1) est taggé Dessert
    # - Scrambled Eggs (id=2) ne l'est pas
    assert 1 in recipe_ids, data
    assert 2 not in recipe_ids, data
