from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class EntradaDiario(BaseModel):
    id: int
    usuario_id: UUID
    fecha: date
    titulo: Optional[str] = None
    contenido: str
    resumen_ia: Optional[str] = None
    emocion_predominante: Optional[str] = None
    categoria_emocional: Optional[str] = None
    promedio_sentimiento: Optional[float] = None
    fuente_modelo: Optional[str] = None
    creado_en: datetime


class CreateEntrada(BaseModel):
    fecha: Optional[date] = None
    titulo: Optional[str] = None
    contenido: str


class UpdateEntrada(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None


class EntradasPage(BaseModel):
    items: List[EntradaDiario]
    page: int
    page_size: int
    total: int
