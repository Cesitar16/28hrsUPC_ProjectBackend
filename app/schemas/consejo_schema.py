from pydantic import BaseModel

class ConsejoInput(BaseModel):
    """
    Schema para una consulta a la base de conocimiento (RAG).
    """
    query: str

    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cómo puedo manejar el estrés de los exámenes?"
            }
        }

class ConsejoResponse(BaseModel):
    """
    Schema para la respuesta de la consulta.
    """
    respuesta: str