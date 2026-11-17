from sqlalchemy import select

from swafy_api.models import User, UserRole


def register(client, email="citizen@example.com", password="correct-horse-battery"):
    return client.post(
        "/api/v1/auth/register",
        json={"display_name": " Amira Ben Ali ", "email": email, "password": password},
    )


def test_register_creates_citizen_and_returns_contract_shape(client, db_session):
    response = register(client)
    assert response.status_code == 201
    payload = response.json()
    assert set(payload) == {"user", "tokens"}
    assert payload["user"]["display_name"] == "Amira Ben Ali"
    assert payload["user"]["email"] == "citizen@example.com"
    assert payload["user"]["role"] == "citizen"
    assert payload["tokens"]["token_type"] == "Bearer"
    assert payload["tokens"]["expires_in"] == 900
    stored = db_session.scalar(select(User).where(User.email == "citizen@example.com"))
    assert stored is not None
    assert stored.role == UserRole.CITIZEN
    assert stored.password_hash != "correct-horse-battery"


def test_registration_cannot_escalate_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Mallory",
            "email": "mallory@example.com",
            "password": "correct-horse-battery",
            "role": "municipal_admin",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_duplicate_email_is_conflict_and_email_is_case_normalized(client):
    assert register(client, "Citizen@Example.com").status_code == 201
    duplicate = register(client, "citizen@example.com")
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "CONFLICT"


def test_login_and_invalid_password(client):
    assert register(client).status_code == 201
    good = client.post(
        "/api/v1/auth/login",
        json={"email": "CITIZEN@example.com", "password": "correct-horse-battery"},
    )
    assert good.status_code == 200
    bad = client.post(
        "/api/v1/auth/login",
        json={"email": "citizen@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "UNAUTHORIZED"


def test_refresh_rotates_token_and_rejects_replay(client):
    initial = register(client).json()
    old_refresh = initial["tokens"]["refresh_token"]
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refreshed.status_code == 200
    new_refresh = refreshed.json()["tokens"]["refresh_token"]
    assert new_refresh != old_refresh

    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert replay.status_code == 401

    success = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert success.status_code == 200


def test_logout_revokes_refresh_token_and_is_idempotent(client):
    tokens = register(client).json()["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    body = {"refresh_token": tokens["refresh_token"]}

    first = client.post("/api/v1/auth/logout", json=body, headers=headers)
    assert first.status_code == 204
    second = client.post("/api/v1/auth/logout", json=body, headers=headers)
    assert second.status_code == 204
    refresh_after_logout = client.post("/api/v1/auth/refresh", json=body)
    assert refresh_after_logout.status_code == 401


def test_logout_requires_access_token(client):
    tokens = register(client).json()["tokens"]
    response = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 401
