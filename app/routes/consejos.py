from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user, get_optional_user
from app.core.errors import raise_http_error
from app.core.settings import get_settings
from app.core.supabase import get_anon_client, get_service_client, get_user_client
from app.schemas import (
    AssignDesafioUsuario,
    CreateDesafio,
    CreateRecomendacion,
    DesafioBienestar,
    DesafioUsuario,
    DesafiosPage,
    DesafiosUsuarioList,
    RecomendacionBienestar,
    RecomendacionesPage,
)

router = APIRouter(prefix="/consejos", tags=["Consejos"])

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _paginate(page: int, page_size: int) -> tuple[int, int, int, int]:
    current_page = max(page, 1)
    size = max(1, min(page_size, MAX_PAGE_SIZE))
    start = (current_page - 1) * size
    end = start + size - 1
    return current_page, size, start, end


@router.get("/recomendaciones", response_model=RecomendacionesPage, summary="Listar recomendaciones")
async def list_recommendations(
    categoria: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
) -> RecomendacionesPage:
    page, page_size, start, end = _paginate(page, page_size)
    client = get_user_client(current_user.token) if current_user else get_anon_client()

    def _fetch() -> tuple[list[dict], int]:
        query = client.table("recomendaciones_bienestar").select("*", count="exact")
        if categoria:
            query = query.eq("categoria", categoria)
        if q:
            pattern = f"%{q}%"
            query = query.or_(
                f"titulo.ilike.{pattern},fuente.ilike.{pattern}"
            )
        response = query.order("fecha_publicacion", desc=True).range(start, end).execute()
        total = response.count or 0
        return response.data or [], total

    data, total = await run_in_threadpool(_fetch)
    items = [RecomendacionBienestar(**item) for item in data]
    return RecomendacionesPage(items=items, page=page, page_size=page_size, total=total)


@router.post("/recomendaciones", response_model=RecomendacionBienestar, summary="Crear recomendación")
async def create_recommendation(
    payload: CreateRecomendacion,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> RecomendacionBienestar:
    # Se requiere autenticación; asumimos que la autorización adicional se maneja externamente.
    settings = get_settings()
    client = get_service_client(settings)

    insert_payload = payload.dict(exclude_unset=True)

    def _insert() -> dict | None:
        response = client.table("recomendaciones_bienestar").insert(insert_payload).execute()
        return response.data[0] if response.data else None

    created = await run_in_threadpool(_insert)
    if not created:
        raise_http_error(500, "internal_error", "No se pudo crear la recomendación.")
    return RecomendacionBienestar(**created)


@router.get("/desafios", response_model=DesafiosPage, summary="Listar desafíos de bienestar")
async def list_challenges(
    dificultad: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_user),
) -> DesafiosPage:
    page, page_size, start, end = _paginate(page, page_size)
    client = get_user_client(current_user.token) if current_user else get_anon_client()

    def _fetch() -> tuple[list[dict], int]:
        query = client.table("desafios_bienestar").select("*", count="exact")
        if dificultad:
            query = query.eq("dificultad", dificultad)
        response = query.order("fecha_creacion", desc=True).range(start, end).execute()
        total = response.count or 0
        return response.data or [], total

    data, total = await run_in_threadpool(_fetch)
    items = [DesafioBienestar(**item) for item in data]
    return DesafiosPage(items=items, page=page, page_size=page_size, total=total)


@router.post("/desafios", response_model=DesafioBienestar, summary="Crear desafío")
async def create_challenge(
    payload: CreateDesafio,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DesafioBienestar:
    settings = get_settings()
    client = get_service_client(settings)

    insert_payload = payload.dict(exclude_unset=True)

    def _insert() -> dict | None:
        response = client.table("desafios_bienestar").insert(insert_payload).execute()
        return response.data[0] if response.data else None

    created = await run_in_threadpool(_insert)
    if not created:
        raise_http_error(500, "internal_error", "No se pudo crear el desafío.")
    return DesafioBienestar(**created)


@router.post(
    "/desafios-usuario",
    response_model=DesafioUsuario,
    summary="Asignar un desafío al usuario",
)
async def assign_challenge(
    payload: AssignDesafioUsuario,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DesafioUsuario:
    client = get_user_client(current_user.token)

    insert_payload = {
        "usuario_id": current_user.user_id,
        "desafio_id": payload.desafio_id,
    }

    def _insert() -> dict | None:
        response = client.table("desafios_usuario").insert(insert_payload).execute()
        if getattr(response, "error", None):
            raise RuntimeError(str(response.error))
        return response.data[0] if response.data else None

    try:
        assignment = await run_in_threadpool(_insert)
    except RuntimeError as exc:
        raise_http_error(409, "conflict", "El desafío ya fue asignado.", details=str(exc))

    if not assignment:
        raise_http_error(500, "internal_error", "No se pudo asignar el desafío.")
    return DesafioUsuario(**assignment)


@router.patch(
    "/desafios-usuario/{assignment_id}/completar",
    response_model=DesafioUsuario,
    summary="Marcar desafío como completado",
)
async def complete_challenge(
    assignment_id: int = Path(..., ge=1),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DesafioUsuario:
    client = get_user_client(current_user.token)

    def _update() -> dict | None:
        client.table("desafios_usuario").update({"completado": True}).eq("id", assignment_id).eq(
            "usuario_id", current_user.user_id
        ).execute()
        response = (
            client.table("desafios_usuario")
            .select("*")
            .eq("id", assignment_id)
            .eq("usuario_id", current_user.user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    assignment = await run_in_threadpool(_update)
    if not assignment:
        raise_http_error(404, "not_found", "Asignación no encontrada.")
    return DesafioUsuario(**assignment)


@router.get("/desafios-usuario", response_model=DesafiosUsuarioList, summary="Listar desafíos del usuario")
async def list_user_challenges(
    completado: Optional[bool] = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DesafiosUsuarioList:
    client = get_user_client(current_user.token)

    def _fetch() -> list[dict]:
        query = client.table("desafios_usuario").select("*").eq("usuario_id", current_user.user_id)
        if completado is not None:
            query = query.eq("completado", completado)
        response = query.order("id", desc=True).execute()
        return response.data or []

    data = await run_in_threadpool(_fetch)
    items = [DesafioUsuario(**item) for item in data]
    return DesafiosUsuarioList(items=items)
