from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../infra/env/api.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SWAFY API"
    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://swafy:swafy-dev-password@localhost:5432/swafy"
    jwt_secret: SecretStr = SecretStr("dev-only-change-this-jwt-secret")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "swafy-api"
    jwt_audience: str = "swafy-client"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    worker_service_token: SecretStr = SecretStr("dev-only-change-this-worker-token")
    cors_origins: str = "http://localhost:5173,http://localhost:8081"
    log_level: str = "INFO"

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_lifetime(cls, value: int) -> int:
        if not 1 <= value <= 60:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 60")
        return value

    @field_validator("refresh_token_expire_days")
    @classmethod
    def validate_refresh_lifetime(cls, value: int) -> int:
        if not 1 <= value <= 90:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be between 1 and 90")
        return value

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("This implementation currently supports HS256 only")
        return value

    @model_validator(mode="after")
    def require_real_production_secrets(self) -> Settings:
        if self.environment == "production":
            jwt_secret = self.jwt_secret.get_secret_value()
            worker_secret = self.worker_service_token.get_secret_value()
            placeholders = ("change-me", "dev-only", "example", "secret")
            for name, secret in (
                ("JWT_SECRET", jwt_secret),
                ("WORKER_SERVICE_TOKEN", worker_secret),
            ):
                if len(secret) < 32 or any(marker in secret.lower() for marker in placeholders):
                    raise ValueError(
                        f"{name} must be a unique random secret of at least 32 characters"
                    )
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def normalize_database_url(url: str) -> str:
    """Prefer psycopg 3 even when a plain postgresql:// URL is supplied."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
