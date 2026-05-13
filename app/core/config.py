"""Application configuration."""
from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task 1 Backend"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    LOG_STDOUT_ENABLED: bool = True
    JWT_SECRET: SecretStr

    FROM_EMAIL: str
    APP_PASSWORD: SecretStr

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "cakf-task1-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: str = ""
    OTEL_EXPORTER_OTLP_LOGS_ENDPOINT: str = ""
    OTEL_TRACES_ENABLED: bool = True
    OTEL_LOGS_ENABLED: bool = True

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_SERVICE_SID: str
    TWILIO_SENDER_PHONE: str

    GOOGLE_CLIENT_ID: str
    FRONTEND_URL: str = "http://localhost:5173"

    DB_URL: str

    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "fastapi_db"
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def populate_db_url(self) -> "Settings":
        if not self.DB_URL:
            self.DB_URL = self.DATABASE_URL
        if not self.DB_URL:
            raise ValueError("DB_URL or DATABASE_URL must be set")
        return self

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
