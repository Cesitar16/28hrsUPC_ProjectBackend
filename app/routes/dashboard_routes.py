from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import app.services.metricas_service as metricas_service
from app.core.auth_deps import AuthUser

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
    """
    try:
        metricas = metricas_service.calcular_metricas_dashboard(usuario_id)
        if "error" in metricas:
            raise HTTPException(status_code=500, detail=metricas["error"])
        
        return metricas

    except Exception as e:
        print(f"Error en /dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")