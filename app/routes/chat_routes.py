from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import uuid
import app.services.chat_service as chat_service
import app.services.user_service as user_service
from app.schemas.chat_schema import MensajeInput, MensajeResponse
from app.agents.conversational_agent import ConversationalAgent
from app.core.auth_deps import AuthUser

router = APIRouter()

try:
    agente_ia = ConversationalAgent()
except ValueError as e:
    print(f"Error al inicializar ConversationalAgent: {e}")
    agente_ia = None

# ENDPOINTS - CHAT (Con RAG)
@router.post(
    "/chat/invoke",
    response_model=Dict[str, Any],
    summary="Invocar al chatbot (Auri)",
    tags=["Chat"]
)

def invocar_chat(
    usuario_id: str = AuthUser, 
    mensaje: MensajeInput = Body(...)
):
    """
    Recibe un mensaje del usuario y devuelve una respuesta de la IA.
    El 'usuario_id' se obtiene automáticamente del Token.
    """
    if not agente_ia:
        raise HTTPException(status_code=500, detail="Agente de IA no inicializado.")

    try:
        datos_usuario = user_service.obtener_usuario_por_id(usuario_id)
        if not datos_usuario:
             raise HTTPException(status_code=404, detail="Usuario no encontrado en la tabla 'usuarios'.")

        historial_db = chat_service.obtener_historial(usuario_id)
        
        respuesta_ia = agente_ia.invoke(
            texto_usuario=mensaje.texto,
            datos_usuario=datos_usuario,
            historial_chat=historial_db
        )

        chat_service.guardar_mensaje(usuario_id, "user", mensaje.texto)
        chat_service.guardar_mensaje(usuario_id, "assistant", respuesta_ia)

        return {"respuesta": respuesta_ia}

    except Exception as e:
        print(f"Error en /chat/invoke: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")

@router.get(
    "/chat/history",
    response_model=List[MensajeResponse],
    summary="Obtener historial de chat",
    tags=["Chat"]
)

def obtener_historial_chat_endpoint(
    usuario_id: str = AuthUser
):
    """
    Obtiene el historial de chat del usuario autenticado.
    """
    try:
        historial = chat_service.obtener_historial(usuario_id=usuario_id)
        return historial
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))