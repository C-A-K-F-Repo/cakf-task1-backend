from __future__ import annotations

from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.api.routes import auth as auth_routes
from app.dependencies.user import get_current_user, allow_staff
from app.dependencies.db import SessionDep
from app.main import app
from uuid import UUID


def test_health_endpoint(client):
    response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ===== /auth/refresh endpoint tests =====

def test_refresh_invalid_token(client, monkeypatch):
    """Test refresh with invalid token"""
    def fake_verify_refresh_token(token):
        raise ValueError("Invalid token")
    
    monkeypatch.setattr("app.core.security.verify_refresh_token", fake_verify_refresh_token)
    
    response = client.post("/api/v1/auth/refresh?refresh_token=invalid_token")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


# ===== /auth/me endpoint tests =====

def test_me_endpoint_unauthorized(client):
    """Test /auth/me without valid token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


# ===== /auth/email/verify endpoint tests =====

def test_email_verify_success(client, monkeypatch):
    """Test successful email verification"""
    async def fake_verify_token(db, token):
        return True
    
    monkeypatch.setattr(auth_routes.email_service, "verify_token", fake_verify_token)
    
    response = client.post("/api/v1/auth/email/verify?token=valid_token")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified"


def test_email_verify_failure(client, monkeypatch):
    """Test email verification with invalid token"""
    async def fake_verify_token(db, token):
        return False
    
    monkeypatch.setattr(auth_routes.email_service, "verify_token", fake_verify_token)
    
    response = client.post("/api/v1/auth/email/verify?token=invalid_token")
    
    assert response.status_code == 400
    assert "failed to verify email" in response.json()["detail"]


# ===== /auth/email/request endpoint tests =====

def test_email_request_success(client, monkeypatch):
    """Test successful verification email request"""
    def fake_get_current_user_override():
        return {
            "sub": "123",
            "email": "user@example.com",
            "role": "User"
        }
    
    async def fake_send_verification_email(email):
        pass
    
    app.dependency_overrides[get_current_user] = fake_get_current_user_override
    monkeypatch.setattr(auth_routes.email_service, "send_verification_email", fake_send_verification_email)
    
    try:
        response = client.get("/api/v1/auth/email/request")
        assert response.status_code == 200
        assert response.json()["message"] == "Email verification sent"
    finally:
        app.dependency_overrides.clear()


def test_email_request_unauthorized(client):
    """Test email request without authorization"""
    response = client.get("/api/v1/auth/email/request")
    
    assert response.status_code == 401


# ===== /auth/staff-only endpoint tests =====

def test_staff_only_allowed(client):
    """Test staff-only endpoint with admin user"""
    def fake_get_current_user_override():
        return {
            "sub": "123",
            "email": "admin@example.com",
            "role": "Administrator"
        }
    
    app.dependency_overrides[get_current_user] = fake_get_current_user_override
    app.dependency_overrides[allow_staff] = lambda: True
    
    try:
        response = client.get("/api/v1/auth/staff-only")
        assert response.status_code == 200
        assert "Accessed as admin" in response.json()["message"]
    finally:
        app.dependency_overrides.clear()


def test_staff_only_denied(client):
    """Test staff-only endpoint with regular user"""
    def fake_get_current_user_override():
        return {
            "sub": "456",
            "email": "user@example.com",
            "role": "User"
        }
    
    def raise_forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")
    
    app.dependency_overrides[get_current_user] = fake_get_current_user_override
    app.dependency_overrides[allow_staff] = raise_forbidden
    
    try:
        response = client.get("/api/v1/auth/staff-only")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


# ===== /auth/google/callback endpoint tests =====

def test_google_callback_new_user_success(client, monkeypatch):
    """Test Google OAuth callback creating new user"""
    def fake_verify_oauth2_token(token, request, client_id):
        return {
            "email": "newuser@gmail.com",
            "email_verified": True
        }
    
    class FakeUser:
        id = UUID("123e4567-e89b-12d3-a456-426614174000")
        email = "newuser@gmail.com"
        role = type('obj', (object,), {'value': 'User'})()
    
    async def fake_get_by_email(self, email):
        if email == "newuser@gmail.com":
            return None
        return FakeUser()
    
    async def fake_create_from_oauth(self, email):
        return FakeUser()
    
    def fake_create_access_token(data):
        return "google_access_token_123"
    
    def fake_create_refresh_token(data):
        return "google_refresh_token_456"
    
    async def fake_session_dep():
        return None
    
    monkeypatch.setattr("google.oauth2.id_token.verify_oauth2_token", fake_verify_oauth2_token)
    monkeypatch.setattr("app.repositories.user.UserRepository.get_by_email", fake_get_by_email)
    monkeypatch.setattr("app.repositories.user.UserRepository.create_from_oauth", fake_create_from_oauth)
    monkeypatch.setattr(auth_routes, "create_access_token", fake_create_access_token)
    monkeypatch.setattr(auth_routes, "create_refresh_token", fake_create_refresh_token)
    app.dependency_overrides[SessionDep] = fake_session_dep
    
    try:
        response = client.post("/api/v1/auth/google/callback", json={"id_token": "valid_google_token"})
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "google_access_token_123"
        assert data["refresh_token"] == "google_refresh_token_456"
    finally:
        app.dependency_overrides.clear()


def test_google_callback_existing_user(client, monkeypatch):
    """Test Google OAuth callback with existing user"""
    def fake_verify_oauth2_token(token, request, client_id):
        return {
            "email": "existing@gmail.com",
            "email_verified": True
        }
    
    class FakeUser:
        id = UUID("987e6543-e89b-12d3-a456-426614174111")
        email = "existing@gmail.com"
        role = type('obj', (object,), {'value': 'User'})()
    
    async def fake_get_by_email(self, email):
        if email == "existing@gmail.com":
            return FakeUser()
        return None
    
    def fake_create_access_token(data):
        return "existing_access_token_789"
    
    def fake_create_refresh_token(data):
        return "existing_refresh_token_101"
    
    async def fake_session_dep():
        return None
    
    monkeypatch.setattr("google.oauth2.id_token.verify_oauth2_token", fake_verify_oauth2_token)
    monkeypatch.setattr("app.repositories.user.UserRepository.get_by_email", fake_get_by_email)
    monkeypatch.setattr(auth_routes, "create_access_token", fake_create_access_token)
    monkeypatch.setattr(auth_routes, "create_refresh_token", fake_create_refresh_token)
    app.dependency_overrides[SessionDep] = fake_session_dep
    
    try:
        response = client.post("/api/v1/auth/google/callback", json={"id_token": "valid_google_token"})
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "existing_access_token_789"
    finally:
        app.dependency_overrides.clear()


def test_google_callback_unverified_email(client, monkeypatch):
    """Test Google OAuth callback with unverified email"""
    def fake_verify_oauth2_token(token, request, client_id):
        return {
            "email": "unverified@gmail.com",
            "email_verified": False
        }
    
    async def fake_session_dep():
        return None
    
    monkeypatch.setattr("google.oauth2.id_token.verify_oauth2_token", fake_verify_oauth2_token)
    app.dependency_overrides[SessionDep] = fake_session_dep
    
    try:
        response = client.post("/api/v1/auth/google/callback", json={"id_token": "unverified_token"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Email not verified"
    finally:
        app.dependency_overrides.clear()


def test_google_callback_invalid_token(client, monkeypatch):
    """Test Google OAuth callback with invalid token"""
    from google.auth.exceptions import GoogleAuthError
    
    def fake_verify_oauth2_token(token, request, client_id):
        raise GoogleAuthError("Invalid token")
    
    async def fake_session_dep():
        return None
    
    monkeypatch.setattr("google.oauth2.id_token.verify_oauth2_token", fake_verify_oauth2_token)
    app.dependency_overrides[SessionDep] = fake_session_dep
    
    try:
        response = client.post("/api/v1/auth/google/callback", json={"id_token": "invalid_token"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
    finally:
        app.dependency_overrides.clear()
