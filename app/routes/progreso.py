from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.supabase import get_user_client
from app.schemas import ProgresoUsuario

router = APIRouter(prefix="/progreso", tags=["Progreso"])


@router.get("", response_model=ProgresoUsuario, summary="Obtener progreso del usuario")
async def get_progress(current_user: AuthenticatedUser = Depends(get_current_user)) -> ProgresoUsuario:
    client = get_user_client(current_user.token)

    def _fetch() -> dict | None:
        response = (
            client.table("vista_progreso_usuario")
            .select("*")
            .eq("usuario_id", current_user.user_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    progress = await run_in_threadpool(_fetch)
    if not progress:
        return ProgresoUsuario(
            usuario_id=current_user.user_id,
            total_reflexiones=0,
            desafios_completados=0,
            interacciones_con_auri=0,
            promedio_sentimiento=None,
            recomendacion_actual=None,
        )
    return ProgresoUsuario(**progress)
