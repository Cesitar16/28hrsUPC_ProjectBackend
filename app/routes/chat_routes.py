from fastapi import APIRouter
from app.agents.openai_agent import responder_mensaje, analizar_sentimiento
from app.core.db_functions import guardar_mensaje, obtener_historial

router = APIRouter(prefix="/chat", tags=["chat"])

# ==========================================================
# 💬 CHAT CON AURI
# ==========================================================

@router.post("/enviar")
def enviar_mensaje(usuario_id: str, texto: str):
    """
    Envía un mensaje del usuario a Auri, analiza la emoción y guarda todo el intercambio.
    """
    # 1️⃣ Analizar sentimiento
    analisis = analizar_sentimiento(texto)
    emocion = analisis["emocion"]
    categoria = analisis["categoria"]
    puntaje = analisis["puntaje"]

    # 2️⃣ Obtener respuesta empática
    respuesta = responder_mensaje(texto)

    # 3️⃣ Guardar mensaje del usuario
    guardar_mensaje(
        usuario_id=usuario_id,
        rol="user",
        texto=texto,
        respuesta=None,
        emocion=emocion,
        categoria=categoria,
        puntaje=puntaje
    )

    # 4️⃣ Guardar respuesta de Auri
    guardar_mensaje(
        usuario_id=usuario_id,
        rol="assistant",
        texto=respuesta,
        respuesta=None
    )

    # 5️⃣ Responder al frontend
    return {
        "usuario_id": usuario_id,
        "texto_usuario": texto,
        "respuesta_auri": respuesta,
        "emocion_detectada": emocion,
        "categoria": categoria,
        "puntaje": puntaje
    }


@router.get("/historial/{usuario_id}")
def historial_chat(usuario_id: str):
    """
    Devuelve el historial completo de mensajes (usuario + Auri).
    """
    data = obtener_historial(usuario_id)
    return {"usuario_id": usuario_id, "mensajes": data}
