from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import app.services.metricas_service as metricas_service
from app.core.auth_deps import AuthUser
# (NUEVO) Importar el nuevo analizador
from app.analysis.dashboard_analyzer import analyze_dashboard_metrics

router = APIRouter()

@router.get(
    "/dashboard",
    response_model=Dict[str, Any],
    summary="Obtener métricas del Dashboard (Protegido)",
    tags=["Dashboard"]
)
def get_dashboard_metrics(
    usuario_id: str = AuthUser 
):
    """
    Calcula y devuelve un resumen de las métricas emocionales
    del usuario (basado en su diario y chat) para poblar el dashboard.

    FLUJO ACTUALIZADO:
    1. Calcula métricas numéricas (conteo, promedios).
    2. Pasa esas métricas a una IA para generar un resumen y recomendación.
    3. Devuelve todo junto.
    """
    try:
        # 1. Calcular métricas base (números)
        metricas_base = metricas_service.calcular_metricas_dashboard(usuario_id)
        if "error" in metricas_base:
            raise HTTPException(status_code=500, detail=metricas_base["error"])
        
        # Si no hay entradas, devolvemos un estado inicial
        if metricas_base.get("total_entradas_diario") == 0:
            return {
                **metricas_base,
                "resumen_ia": "¡Bienvenido a tu dashboard! Escribe tu primera entrada en el diario para ver tus métricas.",
                "recomendacion_ia": "Intenta escribir cómo te sientes hoy."
            }

        # 2. Generar resumen de IA basado en las métricas
        resumen_ia_dict = analyze_dashboard_metrics(metricas_base)
        
        # 3. Combinar los dos diccionarios y devolver
        metricas_completas = {**metricas_base, **resumen_ia_dict}
        
        return metricas_completas

    except Exception as e:
        print(f"Error en /dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")