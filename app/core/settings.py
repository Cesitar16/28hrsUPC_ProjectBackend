from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    supabase_url: AnyHttpUrl
    supabase_anon_key: str
    supabase_service_role_key: Optional[str] = None
    jwt_jwks_url: Optional[AnyHttpUrl] = None
    jwt_audience: Optional[str] = None
    jwt_issuer: Optional[str] = None
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:4321"]
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:  # type: ignore[override]
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        return ["*"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
