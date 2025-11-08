from app.core.supabase_client import supabase
from datetime import datetime
from typing import Optional, Dict, Any, List

# ==========================================================
# 💾 DB FUNCTIONS - Acceso centralizado a la base de datos
# ==========================================================
# Este módulo conecta con las tablas de Supabase a través del cliente HTTP.
# Todas las funciones son reutilizables en los endpoints FastAPI.
# ==========================================================


# ----------------------------------------------------------
# 🧍‍♂️ USUARIOS
# ----------------------------------------------------------
def crear_usuario(nombre: str, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Crea un nuevo usuario en la tabla 'usuarios'.
    """
    data = {"nombre": nombre, "email": email}
    res = supabase.table("usuarios").insert(data).execute()
    return res.data[0] if res.data else None


def obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario existente por correo electrónico.
    """
    res = supabase.table("usuarios").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None


# ----------------------------------------------------------
# 💬 MENSAJES CHAT
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# 📓 ENTRADAS DE DIARIO
# ----------------------------------------------------------
def guardar_entrada_diario(
    usuario_id: str,
    contenido: str,
    resumen: str,
    emocion: str,
    categoria: str,
    promedio_sentimiento: float,
    titulo: Optional[str] = None
):
    """
    Guarda una entrada completa del diario con su resumen y análisis emocional.
    """
    data = {
        "usuario_id": usuario_id,
        "titulo": titulo,
        "contenido": contenido,
        "resumen_ia": resumen,
        "emocion_predominante": emocion,
        "categoria_emocional": categoria,
        "promedio_sentimiento": promedio_sentimiento,
        "fecha": datetime.now().date().isoformat()
    }
    supabase.table("entradas_diario").insert(data).execute()


def obtener_entradas_diario(usuario_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve todas las entradas del diario de un usuario.
    """
    res = supabase.table("entradas_diario").select("*").eq("usuario_id", usuario_id).order("fecha", desc=True).execute()
    return res.data or []


# ----------------------------------------------------------
# 📊 MÉTRICAS EMOCIONALES
# ----------------------------------------------------------
def guardar_metricas_emocionales(
    usuario_id: str,
    periodo: str,
    proporciones: Dict[str, float],
    promedio_sentimiento: float,
    resumen_periodo: str,
    recomendacion_general: str
):
    """
    Inserta o actualiza métricas agregadas (semana o mes) para un usuario.
    """
    data = {
        "usuario_id": usuario_id,
        "periodo": periodo,
        "emociones_predominantes": proporciones,
        "promedio_sentimiento": promedio_sentimiento,
        "resumen_periodo": resumen_periodo,
        "recomendacion_general": recomendacion_general,
        "actualizado_en": datetime.now().isoformat()
    }
    supabase.table("metricas_emocionales").insert(data).execute()


def obtener_ultima_metrica(usuario_id: str) -> Optional[Dict[str, Any]]:
    """
    Devuelve la métrica emocional más reciente del usuario.
    """
    res = supabase.table("metricas_emocionales").select("*").eq("usuario_id", usuario_id).order("actualizado_en", desc=True).limit(1).execute()
    return res.data[0] if res.data else None


# ----------------------------------------------------------
# 🧘‍♀️ ACTIVIDADES DE BIENESTAR
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# ⭐ FEEDBACK DE USUARIO
# ----------------------------------------------------------
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
