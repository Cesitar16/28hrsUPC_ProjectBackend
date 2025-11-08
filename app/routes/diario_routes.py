from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
import uuid
import app.services.diario_service as diario_service
from app.schemas.diario_schema import EntradaDiarioCreate, EntradaDiarioResponse
from app.core.auth_deps import AuthUser

router = APIRouter()
# ENDPOINTS - DIARIO
@router.post(
    "/diario",
    response_model=EntradaDiarioResponse,
    summary="Crear una nueva entrada de diario",
    tags=["Diario"]
)

def crear_entrada_diario_endpoint(
    usuario_id: str = AuthUser,
    entrada: EntradaDiarioCreate = Body(...)
):
    """
    Crea una nueva entrada en el diario.
    El 'usuario_id' se obtiene automáticamente del Token de autenticación.
    """
    try:
        nueva_entrada = diario_service.crear_entrada_diario(
            usuario_id=usuario_id, # Usamos el ID del token
            contenido=entrada.contenido,
            titulo=entrada.titulo
        )
        if not nueva_entrada:
            raise HTTPException(status_code=500, detail="Error al crear la entrada.")
        return nueva_entrada
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/diario",
    response_model=List[EntradaDiarioResponse],
    summary="Obtener historial de entradas de diario",
    tags=["Diario"]
)
def obtener_entradas_diario_endpoint(
    usuario_id: str = AuthUser
):
    """
    Obtiene todas las entradas del diario para un usuario específico,
    ordenadas por fecha descendente.
    """
    try:
        entradas = diario_service.obtener_entradas_diario(usuario_id=usuario_id)
        return entradas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))