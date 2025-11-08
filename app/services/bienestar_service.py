from app.core.supabase_client import supabase
from datetime import datetime

def agregar_actividad(usuario_id: str, tipo: str, descripcion: str):
    """
    Registra una actividad recomendada por la IA.
    """
    data = {
        "usuario_id": usuario_id,
        "tipo_actividad": tipo,
        "descripcion": descripcion,
        "fecha_asignacion": datetime.now().date().isoformat(),
        "completado": False
    }
    supabase.table("actividades_bienestar").insert(data).execute()


def marcar_actividad_completada(actividad_id: int):
    """
    Marca una actividad como completada.
    """
    supabase.table("actividades_bienestar").update({"completado": True}).eq("id", actividad_id).execute()