import os

os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("PERSONAL_DATA_ENCRYPTION_KEY", "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=")
os.environ.setdefault("PERSONAL_DATA_LOOKUP_KEY", "ZmVkY2JhOTg3NjU0MzIxMGZlZGNiYTk4NzY1NDMyMTA=")
os.environ.setdefault("FROM_EMAIL", "test@example.com")
os.environ.setdefault("APP_PASSWORD", "test-app-password")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test-twilio-auth-token")
os.environ.setdefault("TWILIO_SERVICE_SID", "VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
os.environ.setdefault("TWILIO_SENDER_PHONE", "+12025550123")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id.apps.googleusercontent.com")
os.environ.setdefault("DB_URL", "postgresql+asyncpg://user:password@localhost:5432/test_db")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
