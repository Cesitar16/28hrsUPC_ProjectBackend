from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, conint


class FeedbackUsuario(BaseModel):
    id: int
    usuario_id: UUID
    mensaje_id: int
    puntuacion: conint(ge=1, le=5)  # type: ignore[valid-type]
    comentario: Optional[str] = None
    creado_en: datetime


class CreateFeedback(BaseModel):
    mensaje_id: int
    puntuacion: conint(ge=1, le=5)  # type: ignore[valid-type]
    comentario: Optional[str] = None
