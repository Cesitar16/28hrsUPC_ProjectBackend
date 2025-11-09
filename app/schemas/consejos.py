from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class RecomendacionBienestar(BaseModel):
    id: int
    titulo: str
    fuente: Optional[str] = None
    url: Optional[HttpUrl] = None
    categoria: Optional[str] = None
    fecha_publicacion: date


class DesafioBienestar(BaseModel):
    id: int
    descripcion: str
    icono: Optional[str] = None
    dificultad: str
    fecha_creacion: date


class DesafioUsuario(BaseModel):
    id: int
    usuario_id: UUID
    desafio_id: int
    completado: bool
    fecha_completado: Optional[datetime] = None


class CreateRecomendacion(BaseModel):
    titulo: str
    fuente: Optional[str] = None
    url: Optional[HttpUrl] = None
    categoria: Optional[str] = None


class CreateDesafio(BaseModel):
    descripcion: str
    icono: Optional[str] = None
    dificultad: str


class AssignDesafioUsuario(BaseModel):
    desafio_id: int


class RecomendacionesPage(BaseModel):
    items: List[RecomendacionBienestar]
    page: int
    page_size: int
    total: int


class DesafiosPage(BaseModel):
    items: List[DesafioBienestar]
    page: int
    page_size: int
    total: int


class DesafiosUsuarioList(BaseModel):
    items: List[DesafioUsuario]
