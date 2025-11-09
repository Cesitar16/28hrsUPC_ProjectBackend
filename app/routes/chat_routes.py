from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import app.services.chat_service as chat_service
import app.services.user_service as user_service
from app.schemas.chat_schema import MensajeInput, MensajeResponse
from app.agents.conversational_agent import ConversationalAgent
from app.core.auth_deps import AuthUser

router = APIRouter()

# ===========================================================
#   INICIALIZACIÓN DEL AGENTE
# ===========================================================

try:
    agente_ia = ConversationalAgent()
except ValueError as e:
    print(f"Error al inicializar ConversationalAgent: {e}")
    agente_ia = None


# ===========================================================
#   ENDPOINT DE INVOCACIÓN DEL CHAT
# ===========================================================

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
    FLUJO CORREGIDO:
    1. Guardar mensaje del usuario
    2. Obtener historial COMPLETO (con el mensaje recién guardado)
    3. Invocar al agente con historial real
    4. Guardar respuesta
    """

    if not agente_ia:
        raise HTTPException(status_code=500, detail="Agente de IA no inicializado.")

    try:
        # =======================
        #   1. Obtener datos del usuario
        # =======================
        datos_usuario = user_service.obtener_usuario_por_id(usuario_id)
        if not datos_usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        # =======================
        #   2. Guardar PRIMERO el mensaje del usuario
        # =======================
        chat_service.guardar_mensaje(usuario_id, "user", mensaje.texto)

        # =======================
        #   3. Obtener historial completo (incluye el mensaje recién guardado)
        # =======================
        historial = chat_service.obtener_historial(usuario_id)
        print("📌 HISTORIAL NORMALIZADO ENVIADO AL AGENTE →", historial)

        # =======================
        #   4. Invocar al agente con historial actualizado
        # =======================
        respuesta_ia = agente_ia.invoke(
            texto_usuario=mensaje.texto,
            datos_usuario=datos_usuario,
            historial_chat_db=historial
        )

        # =======================
        #   5. Guardar la respuesta de la IA
        # =======================
        chat_service.guardar_mensaje(usuario_id, "assistant", respuesta_ia)

        return {"respuesta": respuesta_ia}

    except Exception as e:
        print(f"❌ Error en /chat/invoke:", e)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# ===========================================================
#   ENDPOINT DE HISTORIAL
# ===========================================================

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
    Devuelve historial normalizado listo para frontend.
    """

    try:
        historial = chat_service.obtener_historial(usuario_id)
        return historial

    except Exception as e:
        print("❌ Error al obtener historial:", e)
        raise HTTPException(status_code=500, detail=str(e))
