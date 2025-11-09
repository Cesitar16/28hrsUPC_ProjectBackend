from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import raise_http_error
from app.core.supabase import get_user_client
from app.schemas import MetricaEmocional, UpsertMetrica

router = APIRouter(prefix="/metricas", tags=["Métricas"])


@router.get("/periodo", response_model=MetricaEmocional, summary="Obtener métricas por periodo")
async def get_metric_by_period(
    periodo: str = Query(..., min_length=1),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MetricaEmocional:
    client = get_user_client(current_user.token)

    def _fetch() -> dict | None:
        response = (
            client.table("metricas_emocionales")
            .select("*")
            .eq("usuario_id", current_user.user_id)
            .eq("periodo", periodo)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    metric = await run_in_threadpool(_fetch)
    if not metric:
        raise_http_error(404, "not_found", "No se encontraron métricas para el periodo solicitado.")
    return MetricaEmocional(**metric)


@router.put("/periodo", response_model=MetricaEmocional, summary="Actualizar métricas del periodo")
async def upsert_metric(
    payload: UpsertMetrica,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> MetricaEmocional:
    client = get_user_client(current_user.token)

    insert_payload = {
        "usuario_id": current_user.user_id,
        "periodo": payload.periodo,
    }
    optional_fields = (
        "emociones_predominantes",
        "promedio_sentimiento",
        "resumen_periodo",
        "recomendacion_general",
    )
    for field in optional_fields:
        value = getattr(payload, field)
        if value is not None:
            insert_payload[field] = value

    def _upsert() -> dict | None:
        client.table("metricas_emocionales").upsert(insert_payload, on_conflict="usuario_id,periodo").execute()
        response = (
            client.table("metricas_emocionales")
            .select("*")
            .eq("usuario_id", current_user.user_id)
            .eq("periodo", payload.periodo)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    metric = await run_in_threadpool(_upsert)
    if not metric:
        raise_http_error(500, "internal_error", "No se pudo guardar la métrica.")
    return MetricaEmocional(**metric)
