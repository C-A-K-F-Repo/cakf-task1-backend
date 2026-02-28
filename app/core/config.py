"""Application configuration."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Task 1 Backend")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")


settings = Settings()
