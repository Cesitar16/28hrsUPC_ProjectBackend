import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import json

# Importamos la configuración para obtener la API key
# Asumiremos que tienes un archivo config.py en app/core/
# Si no lo tienes, asegúrate de cargar la variable de entorno OPENAI_API_KEY
try:
    from app.core.config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializamos el cliente de OpenAI
if not OPENAI_API_KEY:
    raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")

client = OpenAI(api_key=OPENAI_API_KEY)
# 1. MODELO DE DATOS DE SALIDA (SCHEMA)# Definimos una estructura Pydantic. OpenAI usará esto para
# garantizarnos que la salida de la IA siempre sea un JSON válido
# que coincide con lo que nuestra base de datos espera.

class DiaryAnalysisResult(BaseModel):
    """
    Modelo de datos para el resultado del análisis de IA de una entrada de diario.
    """
    resumen_ia: str = Field(
        description="Un resumen conciso de 2 o 3 frases de la entrada del diario."
    )
    emocion_predominante: str = Field(
        description="La emoción principal detectada (ej. 'Tristeza', 'Alegría', 'Ansiedad', 'Gratitud', 'Enojo')."
    )
    categoria_emocional: str = Field(
        description="La categoría general de la emoción ('positiva', 'negativa', 'neutra')."
    )
    promedio_sentimiento: float = Field(
        description="Un puntaje de sentimiento de -1.0 (muy negativo) a 1.0 (muy positivo)."
    )
    fuente_modelo: str = Field(
        description="El nombre del modelo de IA que generó este análisis.",
        default="gpt-4o-mini"
    )
# 2. PROMPT DE SISTEMA
SYSTEM_PROMPT = f"""
Eres 'Auri', un asistente de IA especializado en bienestar emocional. 
Tu tarea es analizar una entrada de diario de un usuario. Debes leer el texto 
y extraer la siguiente información:

1.  **resumen_ia**: Un resumen corto (2-3 frases) de lo que el usuario escribió.
2.  **emocion_predominante**: La emoción principal que detectas.
3.  **categoria_emocional**: Clasifica esa emoción como 'positiva', 'negativa' o 'neutra'.
4.  **promedio_sentimiento**: Un puntaje de -1.0 (muy negativo) a 1.0 (muy positivo).

Responde *únicamente* con un objeto JSON válido que siga la estructura 
definida por el siguiente esquema:

{DiaryAnalysisResult.schema_json(indent=2)}
"""
# 3. FUNCIÓN PRINCIPAL DEL ANALIZADOR
def analyze_diary_content(texto: str) -> Optional[dict]:
    """
    Analiza el contenido de una entrada de diario usando OpenAI en modo JSON.

    Args:
        texto: El contenido completo de la entrada del diario del usuario.

    Returns:
        Un diccionario con los campos de DiaryAnalysisResult, o None si falla.
    """
    print(f"[AnalysisService] Iniciando análisis para texto: {texto[:50]}...")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto}
            ],
            temperature=0.5
        )
        
        # Extraemos el contenido JSON de la respuesta
        analysis_json = response.choices[0].message.content
        
        # Validamos y parseamos el JSON usando nuestro modelo Pydantic
        analysis_data = DiaryAnalysisResult.parse_raw(analysis_json)
        
        print(f"[AnalysisService] Análisis completado: {analysis_data.emocion_predominante}")
        
        # Convertimos el modelo Pydantic de nuevo a un diccionario
        # para que el servicio de base de datos pueda usarlo.
        return analysis_data.dict()

    except Exception as e:
        print(f"Error al analizar la entrada del diario: {e}")
        return None