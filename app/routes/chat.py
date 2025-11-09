from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.core.auth import AuthenticatedUser, get_current_user
from app.core.errors import raise_http_error
from app.core.supabase import get_user_client
from app.schemas import AssistantTurn, CreateMensaje, MensajeChat, MensajesList
from app.services.analysis import analyze_chat_message
from app.services.chatbot import generate_assistant_reply

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/mensajes", response_model=MensajesList, summary="Listar mensajes del chat")
async def list_messages(
    current_user: AuthenticatedUser = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
    before_id: Optional[int] = Query(None, ge=1),
) -> MensajesList:
    client = get_user_client(current_user.token)

    def _fetch() -> list[dict]:
        query = client.table("mensajes_chat").select("*").eq("usuario_id", current_user.user_id)
        if before_id is not None:
            query = query.lt("id", before_id)
        response = query.order("id", desc=True).limit(limit).execute()
        return response.data or []

    data = await run_in_threadpool(_fetch)
    ordered = sorted(data, key=lambda item: item["id"])
    return MensajesList(items=[MensajeChat(**item) for item in ordered])


@router.post("/mensajes", response_model=AssistantTurn, summary="Registrar turno de chat")
async def create_message(
    payload: CreateMensaje,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AssistantTurn:
    client = get_user_client(current_user.token)
    user_analysis = analyze_chat_message(payload.texto)

    user_payload = {
        "usuario_id": current_user.user_id,
        "rol": "user",
        "texto": payload.texto,
        "emocion_detectada": (user_analysis.get("emotions") or [None])[0],
        "categoria_emocional": user_analysis.get("category"),
        "puntuacion_sentimiento": user_analysis.get("sentiment"),
        "resumen": user_analysis.get("summary"),
    }

    def _insert_user() -> dict | None:
        response = client.table("mensajes_chat").insert(user_payload).execute()
        return response.data[0] if response.data else None

    user_message = await run_in_threadpool(_insert_user)
    if not user_message:
        raise_http_error(500, "internal_error", "No se pudo registrar el mensaje del usuario.")

    assistant_text, assistant_analysis = generate_assistant_reply(payload.texto)
    assistant_payload = {
        "usuario_id": current_user.user_id,
        "rol": "assistant",
        "texto": assistant_text,
        "emocion_detectada": (assistant_analysis.get("emotions") or [None])[0],
        "categoria_emocional": assistant_analysis.get("category"),
        "puntuacion_sentimiento": assistant_analysis.get("sentiment"),
        "analisis_ia": assistant_analysis,
        "resumen": assistant_analysis.get("summary"),
    }

    def _insert_assistant() -> dict | None:
        response = client.table("mensajes_chat").insert(assistant_payload).execute()
        return response.data[0] if response.data else None

    assistant_message = await run_in_threadpool(_insert_assistant)
    if not assistant_message:
        raise_http_error(500, "internal_error", "No se pudo registrar la respuesta de Auri.")

    return AssistantTurn(
        user_message=MensajeChat(**user_message),
        assistant_message=MensajeChat(**assistant_message),
    )
