"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task 1 Backend"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    FROM_EMAIL:str = "your.email@gmail.com"
    APP_PASSWORD:SecretStr = SecretStr("your_app_password")

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_SERVICE_SID: str
    TWILIO_SENDER_PHONE: str

    DB_URL: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
