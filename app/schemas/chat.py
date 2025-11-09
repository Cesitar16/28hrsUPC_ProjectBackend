from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class MensajeChat(BaseModel):
    id: int
    usuario_id: UUID
    rol: str
    texto: str
    emocion_detectada: Optional[str] = None
    categoria_emocional: Optional[str] = None
    puntuacion_sentimiento: Optional[float] = None
    analisis_ia: Optional[Dict[str, Any]] = None
    fecha: datetime
    resumen: Optional[str] = None


class CreateMensaje(BaseModel):
    texto: str


class AssistantTurn(BaseModel):
    user_message: MensajeChat
    assistant_message: MensajeChat


class MensajesList(BaseModel):
    items: List[MensajeChat]
