from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student_test@example.com",
            "password": "MySecretPassword123"
        }
    )
    
    assert response.status_code == 201

def test_login_user():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "token": "stringstringstri",
            "new_password": "stringst"
        }
    )
    assert response.status_code == 204

def test_password_recovery():
    response = client.post(
        "/api/v1/account-recovery/request",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 204


def test_acc_recovery():
    response = client.post(
        "/api/v1/account-recovery/request",
        json={"email": "user@example.com"}
    )
    assert response.status_code == 204
