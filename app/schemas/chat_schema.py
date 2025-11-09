from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

# 💬 SCHEMAS - MENSAJES DE CHAT

class MensajeInput(BaseModel):
    """
    Schema para un nuevo mensaje (input) del usuario al chat.
    El 'usuario_id' ya no se incluye aquí, se obtiene del token.
    """
    texto: str

    class Config:
        json_schema_extra = {
            "example": {
                "texto": "Hola Auri, ¿cómo estás?"
            }
        }

class MensajeResponse(BaseModel):
    id: int
    usuario_id: uuid.UUID
    rol: str
    texto: str
    emocion_detectada: Optional[str]
    categoria_emocional: Optional[str]
    puntuacion_sentimiento: Optional[float]
    fecha: datetime
    resumen: Optional[str] 

    class Config:
        from_attributes = True