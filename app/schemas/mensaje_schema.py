from pydantic import BaseModel

class MensajeIn(BaseModel):
    usuario: str
    texto: str

class MensajeOut(BaseModel):
    usuario: str
    texto: str
    respuesta: str
