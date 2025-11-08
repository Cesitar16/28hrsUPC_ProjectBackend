from fastapi import APIRouter
from app.agents.openai_agent import responder_mensaje, analizar_sentimiento, generar_resumen_emocional
from app.core.db_functions import (
    guardar_entrada_diario,
    obtener_entradas_diario,
    obtener_ultima_metrica,
    guardar_metricas_emocionales
)
from app.core.metricas import generar_metricas_emocionales
from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter
from app.agents.openai_agent import responder_mensaje, analizar_sentimiento
from app.core.supabase_client import guardar_entrada_diario, generar_metricas_emocionales

router = APIRouter(prefix="/diario", tags=["Diario"])

class EntradaDiario(BaseModel):
    usuario_id: str
    contenido: str

@router.post("/entrada")
def nueva_entrada(data: EntradaDiario):
    try:
        resumen = responder_mensaje(f"Resume este texto con empatía: {data.contenido}")
        analisis = analizar_sentimiento(data.contenido)

        guardar_entrada_diario(
            usuario_id=data.usuario_id,
            contenido=data.contenido,
            resumen=resumen,
            emocion=analisis["emocion"],
            categoria=analisis["categoria"],
            promedio_sentimiento=analisis["puntaje"]
        )

        generar_metricas_emocionales(data.usuario_id)

        return {
            "usuario_id": data.usuario_id,
            "resumen": resumen,
            "emocion_predominante": analisis["emocion"],
            "categoria": analisis["categoria"],
            "promedio_sentimiento": analisis["puntaje"]
        }

    except Exception as e:
        print(f"❌ Error en /diario/entrada: {e}")
        return {"error": str(e)}

@router.get("/entradas/{usuario_id}")
def listar_entradas(usuario_id: str):
    """
    Devuelve todas las entradas de diario del usuario ordenadas por fecha.
    """
    data = obtener_entradas_diario(usuario_id)
    return {"usuario_id": usuario_id, "entradas": data}


@router.get("/resumen/{usuario_id}")
def resumen_emocional(usuario_id: str):
    """
    Devuelve el resumen emocional más reciente del usuario.
    """
    data = obtener_ultima_metrica(usuario_id)
    if not data:
        return {"mensaje": "Aún no hay métricas calculadas."}
    return {
        "usuario_id": usuario_id,
        "periodo": data["periodo"],
        "emociones_predominantes": data["emociones_predominantes"],
        "promedio_sentimiento": data["promedio_sentimiento"],
        "resumen_periodo": data["resumen_periodo"],
        "recomendacion": data["recomendacion_general"],
        "actualizado_en": data["actualizado_en"]
    }


@router.post("/resumen-semanal")
def resumen_semanal(usuario_id: str):
    """
    Genera un resumen emocional global a partir de los mensajes de la semana.
    """
    from app.core.db_functions import obtener_historial

    mensajes = obtener_historial(usuario_id)
    textos_usuario = [m["texto"] for m in mensajes if m["rol"] == "user"]

    if not textos_usuario:
        return {"mensaje": "No hay suficientes datos para generar resumen semanal."}

    resumen = generar_resumen_emocional(textos_usuario)

    # Guardar como nueva métrica
    guardar_metricas_emocionales(
        usuario_id=usuario_id,
        periodo=datetime.now().strftime("%Y-W%U"),
        proporciones={},
        promedio_sentimiento=0.0,
        resumen_periodo=resumen,
        recomendacion_general="Continúa escribiendo para seguir comprendiendo tus emociones."
    )

    return {"usuario_id": usuario_id, "resumen_semanal": resumen}
