from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

#positive

def test_health_check():
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json = {
            "full_name": "string",
            "dob": "2026-05-07T20:06:42.244Z",
            "delivery_address": "string",
            "phone_number": "string",
            "email": "user@example.com",
            "password": "stringst",
            "role": "User"
        }
    )
    
    assert response.status_code == 201

def test_login_user():
    response = client.post(
        "/api/v1/auth/login",
        json = {
            "token": "test_user1@example.com",
            "new_password": "Password123!"
        }
    )
    assert response.status_code == 204

def test_acc_recovery():
    response = client.post(
        "/api/v1/account-recovery/request",
        json = {"email": "test_user1@example.com"}
    )
    assert response.status_code == 204


def test_acc_psswd_recovery():
    response = client.post(
        "/api/v1/account-recovery/reset",
        json = {
            "token": "stringstringstri",
            "new_password": "stringst"
        }
    )
    assert response.status_code == 204

#negative

def test_login_nonexistent_user():
    response = client.post(
        "/api/v1/auth/login",
        json = {
            "email": "nobody@example.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 422

def test_login_wrong_password():
    response = client.post(
        "/api/v1/auth/login",
        json = {
            "email": "test_user1@example.com",
            "password": "Password1234!"
        }
    )
    assert response.status_code == 422

def test_register_existing_user():
    response = client.post(
        "/api/v1/auth/register",
        json = {
            "email": "test_user1@example.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 422

def test_register_invalid_email_format():
    response = client.post(
        "/api/v1/auth/register",
        json = {
            "email": "BIIIG-PENIS",
            "password": "Password123!"
        }
    )
    assert response.status_code == 422

def test_register_wrong_password_format():
    response = client.post(
        json = {
            "emai": "test_user@gmail.com",
            "password": "PENIS"
        }
    )
    assert response.status_code == 422

def test_account_recoery_noexisting_email():
    response = client.post(
        json = {
            "email": "DIGGEST-PENIS-EVER@example.com"
        }
    )
    assert response.status_code == 422

def test_reset_password_wrong_token():
    response = client.post(
        json = {
            "token": "wrong_token",
            "new_password": "stringst"
        }
    )
    assert response.status_code == 422