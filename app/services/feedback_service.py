from app.core.database import supabase
from datetime import datetime
from typing import Optional, Dict, Any, List

def guardar_feedback(usuario_id: str, mensaje_id: int, puntuacion: int, comentario: Optional[str] = None):
    """
    Guarda una valoración del usuario sobre una respuesta de Auri.
    """
    data = {
        "usuario_id": usuario_id,
        "mensaje_id": mensaje_id,
        "puntuacion": puntuacion,
        "comentario": comentario,
        "creado_en": datetime.now().isoformat()
    }
    supabase.table("feedback_usuario").insert(data).execute()


def obtener_feedbacks(usuario_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve todos los feedbacks realizados por un usuario.
    """
    res = supabase.table("feedback_usuario").select("*").eq("usuario_id", usuario_id).order("creado_en", desc=True).execute()
    return res.data or []
