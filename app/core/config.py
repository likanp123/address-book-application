from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and an optional .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="development", alias="APP_ENV")
    db_url: str = Field(default="sqlite:///./address_book.db", alias="DB_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


settings = Settings()

