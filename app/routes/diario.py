from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import raise_http_error
from app.core.supabase import get_user_client
from app.schemas import CreateEntrada, EntradaDiario, EntradasPage, UpdateEntrada
from app.services.analysis import analyze_diary_entry

router = APIRouter(prefix="/diario", tags=["Diario"])

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _paginate_params(page: int, page_size: int) -> tuple[int, int, int, int]:
    current_page = max(page, 1)
    size = max(1, min(page_size, MAX_PAGE_SIZE))
    start = (current_page - 1) * size
    end = start + size - 1
    return current_page, size, start, end


@router.get("", response_model=EntradasPage, summary="Listar entradas del diario")
async def list_entries(
    current_user: AuthenticatedUser = Depends(get_current_user),
    page: int = Query(DEFAULT_PAGE, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    q: Optional[str] = Query(None, description="Filtro de búsqueda por título o contenido"),
) -> EntradasPage:
    client = get_user_client(current_user.token)
    page, page_size, start, end = _paginate_params(page, page_size)

    def _fetch() -> tuple[list[dict], int]:
        query = (
            client.table("entradas_diario")
            .select("*", count="exact")
            .eq("usuario_id", current_user.user_id)
        )
        if from_date:
            query = query.gte("fecha", str(from_date))
        if to_date:
            query = query.lte("fecha", str(to_date))
        if q:
            pattern = f"%{q}%"
            query = query.or_(
                f"titulo.ilike.{pattern},contenido.ilike.{pattern}"
            )
        response = query.order("creado_en", desc=True).range(start, end).execute()
        total = response.count or 0
        return response.data or [], total

    data, total = await run_in_threadpool(_fetch)
    items = [EntradaDiario(**item) for item in data]
    return EntradasPage(items=items, page=page, page_size=page_size, total=total)


@router.post("", response_model=EntradaDiario, summary="Crear una nueva entrada")
async def create_entry(
    payload: CreateEntrada,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> EntradaDiario:
    client = get_user_client(current_user.token)
    analysis = analyze_diary_entry(payload.contenido)
    insert_payload = {
        "usuario_id": current_user.user_id,
        "contenido": payload.contenido,
        **{k: v for k, v in analysis.items() if v is not None},
    }
    if payload.fecha:
        insert_payload["fecha"] = str(payload.fecha)
    if payload.titulo is not None:
        insert_payload["titulo"] = payload.titulo

    def _create() -> dict | None:
        response = client.table("entradas_diario").insert(insert_payload).execute()
        return response.data[0] if response.data else None

    created = await run_in_threadpool(_create)
    if not created:
        raise_http_error(500, "internal_error", "No se pudo crear la entrada.")
    return EntradaDiario(**created)


@router.get("/{entrada_id}", response_model=EntradaDiario, summary="Obtener entrada por ID")
async def get_entry(
    entrada_id: int = Path(..., ge=1),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> EntradaDiario:
    client = get_user_client(current_user.token)

    def _fetch() -> dict | None:
        response = (
            client.table("entradas_diario")
            .select("*")
            .eq("id", entrada_id)
            .eq("usuario_id", current_user.user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    entry = await run_in_threadpool(_fetch)
    if not entry:
        raise_http_error(404, "not_found", "Entrada no encontrada.")
    return EntradaDiario(**entry)


@router.patch("/{entrada_id}", response_model=EntradaDiario, summary="Actualizar entrada")
async def update_entry(
    entrada_id: int = Path(..., ge=1),
    payload: UpdateEntrada = Body(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> EntradaDiario:
    client = get_user_client(current_user.token)
    update_payload = {}
    if payload.titulo is not None:
        update_payload["titulo"] = payload.titulo
    if payload.contenido is not None:
        update_payload["contenido"] = payload.contenido
        analysis = analyze_diary_entry(payload.contenido)
        update_payload.update({k: v for k, v in analysis.items() if v is not None})

    if not update_payload:
        raise_http_error(400, "validation_error", "No se proporcionaron campos para actualizar.")

    def _update() -> dict | None:
        client.table("entradas_diario").update(update_payload).eq("id", entrada_id).eq(
            "usuario_id", current_user.user_id
        ).execute()
        response = (
            client.table("entradas_diario")
            .select("*")
            .eq("id", entrada_id)
            .eq("usuario_id", current_user.user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    entry = await run_in_threadpool(_update)
    if not entry:
        raise_http_error(404, "not_found", "Entrada no encontrada.")
    return EntradaDiario(**entry)


@router.delete("/{entrada_id}", summary="Eliminar entrada")
async def delete_entry(
    entrada_id: int = Path(..., ge=1),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, bool]:
    client = get_user_client(current_user.token)

    def _delete() -> int:
        response = (
            client.table("entradas_diario")
            .delete()
            .eq("id", entrada_id)
            .eq("usuario_id", current_user.user_id)
            .execute()
        )
        return len(response.data or [])

    deleted = await run_in_threadpool(_delete)
    if deleted == 0:
        raise_http_error(404, "not_found", "Entrada no encontrada.")
    return {"deleted": True}
