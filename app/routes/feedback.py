from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import raise_http_error
from app.core.supabase import get_user_client
from app.schemas import CreateFeedback, FeedbackUsuario

router = APIRouter(prefix="/chat/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackUsuario, summary="Registrar feedback de un mensaje")
async def create_feedback(
    payload: CreateFeedback,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FeedbackUsuario:
    client = get_user_client(current_user.token)

    insert_payload = {
        "usuario_id": current_user.user_id,
        "mensaje_id": payload.mensaje_id,
        "puntuacion": int(payload.puntuacion),
    }
    if payload.comentario is not None:
        insert_payload["comentario"] = payload.comentario

    def _create() -> dict | None:
        response = client.table("feedback_usuario").insert(insert_payload).execute()
        if getattr(response, "error", None):
            raise RuntimeError(str(response.error))
        return response.data[0] if response.data else None

    try:
        created = await run_in_threadpool(_create)
    except RuntimeError as exc:
        raise_http_error(409, "conflict", "No se pudo registrar el feedback.", details=str(exc))

    if not created:
        raise_http_error(500, "internal_error", "Respuesta vacía de Supabase.")

    return FeedbackUsuario(**created)
