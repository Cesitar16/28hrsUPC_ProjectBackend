from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import raise_http_error
from app.core.supabase import get_user_client
from app.schemas import MePatch, UserProfile

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=UserProfile, summary="Perfil del usuario actual")
async def get_me(current_user: AuthenticatedUser = Depends(get_current_user)) -> UserProfile:
    client = get_user_client(current_user.token)

    def _fetch() -> dict | None:
        response = client.table("usuarios").select("*").eq("id", current_user.user_id).limit(1).execute()
        return response.data[0] if response.data else None

    profile = await run_in_threadpool(_fetch)
    if not profile:
        raise_http_error(404, "not_found", "Perfil no encontrado.")

    profile.setdefault("email", current_user.email)
    return UserProfile(**profile)


@router.patch("/me", response_model=UserProfile, summary="Actualizar perfil")
async def update_me(
    payload: MePatch,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfile:
    update_payload = {}
    if payload.nombre is not None:
        update_payload["nombre"] = payload.nombre

    if not update_payload:
        raise_http_error(400, "validation_error", "No se proporcionaron campos para actualizar.")

    client = get_user_client(current_user.token)

    def _update() -> dict | None:
        client.table("usuarios").update(update_payload).eq("id", current_user.user_id).execute()
        response = client.table("usuarios").select("*").eq("id", current_user.user_id).limit(1).execute()
        return response.data[0] if response.data else None

    profile = await run_in_threadpool(_update)
    if not profile:
        raise_http_error(404, "not_found", "Perfil no encontrado.")

    profile.setdefault("email", current_user.email)
    return UserProfile(**profile)
