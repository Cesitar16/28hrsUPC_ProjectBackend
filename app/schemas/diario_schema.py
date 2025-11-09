from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
import uuid
# 📓 SCHEMAS - ENTRADAS DE DIARIO
class EntradaDiarioCreate(BaseModel):
    """
    Schema para crear una nueva entrada de diario. 
    Esto es lo que el frontend debe enviar en el body del POST.
    """
    titulo: Optional[str] = None
    contenido: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "titulo": "Un día de reflexión",
                "contenido": "Hoy me sentí un poco abrumado por el trabajo, pero logré terminar mi proyecto principal. Fue un alivio."
            }
        }

class EntradaDiarioResponse(BaseModel):
    """
    Schema para devolver una entrada de diario.
    Coincide con la tabla 'entradas_diario' de Supabase.
    """
    id: int
    usuario_id: uuid.UUID
    fecha: date
    titulo: Optional[str]
    contenido: str
    resumen_ia: Optional[str]
    emocion_predominante: Optional[str]
    categoria_emocional: Optional[str]
    promedio_sentimiento: Optional[float]
    fuente_modelo: Optional[str]
    creado_en: datetime

    class Config:
        from_attributes = True