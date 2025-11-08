from app.core.supabase_client import supabase
from datetime import datetime
from typing import Optional, Dict, Any, List

def guardar_mensaje(
    usuario_id: str,
    rol: str,
    texto: str,
    respuesta: Optional[str] = None,
    emocion: Optional[str] = None,
    categoria: Optional[str] = None,
    puntaje: Optional[float] = None,
):
    """
    Guarda un mensaje (usuario o IA) en la tabla 'mensajes_chat'.
    """
    data = {
        "usuario_id": usuario_id,
        "rol": rol,
        "texto": texto,
        "respuesta": respuesta,
        "emocion_detectada": emocion,
        "categoria_emocional": categoria,
        "puntuacion_sentimiento": puntaje,
        "fecha": datetime.now().isoformat()
    }
    supabase.table("mensajes_chat").insert(data).execute()


def obtener_historial(usuario_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve todos los mensajes (user + Auri) ordenados por fecha descendente.
    """
    res = supabase.table("mensajes_chat").select("*").eq("usuario_id", usuario_id).order("fecha", desc=True).execute()
    return res.data or []

