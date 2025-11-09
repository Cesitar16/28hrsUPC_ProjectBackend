from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProgresoUsuario(BaseModel):
    usuario_id: UUID
    total_reflexiones: int
    desafios_completados: int
    interacciones_con_auri: int
    promedio_sentimiento: Optional[float] = None
    recomendacion_actual: Optional[str] = None
