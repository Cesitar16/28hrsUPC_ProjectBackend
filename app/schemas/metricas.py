from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class MetricaEmocional(BaseModel):
    id: int
    usuario_id: UUID
    periodo: str
    emociones_predominantes: Optional[Dict[str, Any]] = None
    promedio_sentimiento: Optional[float] = None
    resumen_periodo: Optional[str] = None
    recomendacion_general: Optional[str] = None
    actualizado_en: datetime


class UpsertMetrica(BaseModel):
    periodo: str
    emociones_predominantes: Optional[Dict[str, Any]] = None
    promedio_sentimiento: Optional[float] = None
    resumen_periodo: Optional[str] = None
    recomendacion_general: Optional[str] = None
