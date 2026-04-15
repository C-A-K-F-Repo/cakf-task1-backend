"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task 1 Backend"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_SERVICE_SID: str
    TWILIO_SENDER_PHONE: str

    DB_URL: str

    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "fastapi_db"
    DATABASE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
