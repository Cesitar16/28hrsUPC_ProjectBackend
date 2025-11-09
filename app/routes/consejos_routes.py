from fastapi import APIRouter, HTTPException, Body
from app.schemas.consejo_schema import ConsejoInput, ConsejoResponse
from app.agents.rag_service import rag_service_instance
from app.core.auth_deps import AuthUser
from typing import Dict, Any

router = APIRouter()

@router.post(
    "/consejos",
    response_model=ConsejoResponse,
    summary="Buscar en la Base de Conocimiento (RAG)",
    tags=["Consejos (RAG)"]
)
def buscar_consejo(
    usuario_id: str = AuthUser, # Protegemos el endpoint
    consulta: ConsejoInput = Body(...)
):
    """
    Recibe una consulta del usuario y devuelve una respuesta directa
    de la base de conocimiento (RAG).
    """
    if not rag_service_instance or not rag_service_instance.rag_chain:
        raise HTTPException(status_code=500, detail="Servicio RAG no inicializado.")

    try:
        # Usamos el método query_rag que creamos
        respuesta_rag = rag_service_instance.query_rag(consulta.query)
        
        return {"respuesta": respuesta_rag}

    except Exception as e:
        print(f"Error en /consejos: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")