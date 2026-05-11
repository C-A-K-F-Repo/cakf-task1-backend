from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.routes import auth as auth_routes


def test_health_endpoint(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_nonexistent_user_returns_401(client: TestClient, monkeypatch):
    async def fake_login_user(_db, payload):
        raise ValueError("User not found")

    monkeypatch.setattr(auth_routes.auth_service, "login_user", fake_login_user)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "noone@example.com", "password": "Password!123"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "User not found"}
    assert response.headers.get("www-authenticate") == "Bearer"


def test_login_incorrect_password(client: TestClient, monkeypatch):
    async def fake_login_user(_db, payload):
        raise ValueError("Invalid email or password")

    monkeypatch.setattr(auth_routes.auth_service, "login_user", fake_login_user)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "jane@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
    assert response.headers.get("www-authenticate") == "Bearer"


def test_login_successful(client: TestClient, monkeypatch):
    async def fake_login_user(_db, payload):
        return {
            "access_token": "test-access-token-xyz",
            "refresh_token": "test-refresh-token-abc",
            "token_type": "bearer",
        }

    monkeypatch.setattr(auth_routes.auth_service, "login_user", fake_login_user)

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "jane@example.com", "password": "Password!123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "test-access-token-xyz"
    assert body["refresh_token"] == "test-refresh-token-abc"
    assert body["token_type"] == "bearer"


def test_register_successful(client: TestClient, monkeypatch):
    from uuid import UUID

    async def fake_send_verification_email(email: str):
        pass

    async def fake_register_user(_db, payload):
        return {
            "id": UUID("22222222-2222-2222-2222-222222222222"),
            "full_name": payload.full_name,
            "dob": payload.dob,
            "delivery_address": payload.delivery_address,
            "phone_number": payload.phone_number,
            "email": payload.email,
            "role": "User",
        }

    monkeypatch.setattr(auth_routes.email_service, "send_verification_email", fake_send_verification_email)
    monkeypatch.setattr(auth_routes.auth_service, "register_user", fake_register_user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "dob": "1995-05-12T00:00:00",
            "delivery_address": "456 Oak Ave",
            "phone_number": "+12025550456",
            "email": "john@example.com",
            "password": "SecurePass!99",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "john@example.com"
    assert body["full_name"] == "John Doe"
    assert body["role"] == "User"
    assert body["id"] == "22222222-2222-2222-2222-222222222222"


def test_register_weak_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Weak",
            "dob": "2000-01-01T00:00:00",
            "delivery_address": "789 Pine St",
            "phone_number": "+12025550789",
            "email": "weak@example.com",
            "password": "weakpass",
        },
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(
        "Password must contain at least one letter and one special character" in error.get("msg", "")
        for error in errors
    )


def test_register_existing_user(client: TestClient, monkeypatch):
    async def fake_send_verification_email(email: str):
        pass

    async def fake_register_user(_db, payload):
        raise ValueError("User with this email already exists")

    monkeypatch.setattr(auth_routes.email_service, "send_verification_email", fake_send_verification_email)
    monkeypatch.setattr(auth_routes.auth_service, "register_user", fake_register_user)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Duplicate User",
            "dob": "1990-03-15T00:00:00",
            "delivery_address": "321 Elm St",
            "phone_number": "+12025550321",
            "email": "duplicate@example.com",
            "password": "Strong@Pass123",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}
