"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class Settings(BaseSettings):
    PROJECT_NAME: str = "Task 1 Backend"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: SecretStr
    TWILIO_SERVICE_SID: str
    TWILIO_SENDER_PHONE: PhoneNumber

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
