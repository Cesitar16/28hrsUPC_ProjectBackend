from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import HTTPException
from supabase import Client, create_client

from app.core.settings import Settings, get_settings


def _create_client(settings: Settings, api_key: str) -> Client:
    return create_client(str(settings.supabase_url), api_key)


@lru_cache(maxsize=1)
def get_anon_client() -> Client:
    settings = get_settings()
    return _create_client(settings, settings.supabase_anon_key)


def get_service_client(settings: Optional[Settings] = None) -> Client:
    settings = settings or get_settings()
    if not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "internal_error",
                    "message": "Supabase service role no configurada.",
                }
            },
        )
    return _create_client(settings, settings.supabase_service_role_key)


def get_user_client(token: str, settings: Optional[Settings] = None) -> Client:
    settings = settings or get_settings()
    client = _create_client(settings, settings.supabase_anon_key)
    client.postgrest.auth(token)
    return client
