from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.acc_rec_service import acc_rec_service
from app.services.email_notifications import email_service


def test_health_endpoint(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    

def test_account_recovery_successful(client: TestClient, monkeypatch):
    async def fake_send_recovery_email(email: str):
        pass

    class FakeUser:
        id = "user-id-123"
        email = "jane@example.com"

    class FakeRepository:
        def __init__(self, _db):
            pass

        async def get_by_email(self, email):
            if email == "jane@example.com":
                return FakeUser()
            return None

    monkeypatch.setattr(email_service, "send_recovery_email", fake_send_recovery_email)
    monkeypatch.setattr("app.services.acc_rec_service.UserRepository", FakeRepository)

    response = client.post(
        "/api/v1/account-recovery/request",
        json={"email": "jane@example.com"},
    )

    assert response.status_code == 204
    assert response.text == ""


def test_account_recovery_request_user_not_found(client: TestClient, monkeypatch):
    class FakeRepository:
        def __init__(self, _db):
            pass

        async def get_by_email(self, email):
            return None

    monkeypatch.setattr("app.services.acc_rec_service.UserRepository", FakeRepository)

    response = client.post(
        "/api/v1/account-recovery/request",
        json={"email": "nonexistent@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}


def test_password_reset_successful(client: TestClient, monkeypatch):
    async def fake_verify(email: str, code: str) -> bool:
        return email == "jane@example.com" and code == "ABC123"

    class FakeRepository:
        def __init__(self, _db):
            pass

        async def update_password(self, email: str, new_password: str):
            pass

    monkeypatch.setattr(email_service, "verify", fake_verify)
    monkeypatch.setattr("app.services.acc_rec_service.UserRepository", FakeRepository)

    response = client.post(
        "/api/v1/account-recovery/reset",
        json={
            "email": "jane@example.com",
            "code": "ABC123",
            "new_password": "NewSecure@Pass123",
        },
    )

    assert response.status_code == 204
    assert response.text == ""


def test_password_reset_invalid_code(client: TestClient, monkeypatch):
    async def fake_verify(email: str, code: str) -> bool:
        return False

    monkeypatch.setattr(email_service, "verify", fake_verify)

    response = client.post(
        "/api/v1/account-recovery/reset",
        json={
            "email": "jane@example.com",
            "code": "INVALID",
            "new_password": "NewSecure@Pass123",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email not verified"}
