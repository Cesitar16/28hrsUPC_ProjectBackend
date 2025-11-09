import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional
import json

try:
    from app.core.config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")

client = OpenAI(api_key=OPENAI_API_KEY)

# 1. Modelo de datos de Pydantic (sin cambios)
class DashboardAnalysisResult(BaseModel):
    """
    Modelo de datos para el resumen de IA del dashboard.
    """
    resumen_ia: str = Field(
        description="Un resumen cálido y empático (2-3 frases) sobre las métricas emocionales del usuario."
    )
    recomendacion_ia: str = Field(
        description="Un consejo o recomendación breve (1-2 frases) basado en la emoción predominante."
    )
    fuente_modelo: str = Field(
        description="El modelo de IA que generó el resumen.",
        default="gpt-4o-mini"
    )

# 2. (CORREGIDO) Prompt de Sistema Simplificado
SYSTEM_PROMPT = f"""
Eres 'Auri', un asistente de IA especializado en bienestar emocional.
Tu tarea es analizar un resumen de métricas emocionales de un usuario y 
devolver un análisis cálido y empático. NO hables de "métricas" o "datos". 
Habla sobre sus "emociones" y "sentimientos".

El usuario te pasará un JSON con sus métricas. Basado en ese JSON,
genera una respuesta *únicamente* en formato JSON con las siguientes claves:

"resumen_ia": (Un resumen cálido y empático de 2-3 frases sobre las métricas)
"recomendacion_ia": (Un consejo o recomendación breve de 1-2 frases)
"fuente_modelo": "gpt-4o-mini"
"""
# --- Fin de la corrección ---


# 3. Función principal del analizador (sin cambios)
def analyze_dashboard_metrics(metrics: dict) -> Optional[dict]:
    """
    Analiza un diccionario de métricas (calculadas por metricas_service) 
    y genera un resumen de IA.
    """
    print(f"[DashboardAnalyzer] Iniciando resumen de IA para métricas: {metrics}")
    
    # Convertimos las métricas en un string para el prompt
    metrics_json = json.dumps(metrics)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": metrics_json}
            ],
            temperature=0.7
        )
        
        analysis_json = response.choices[0].message.content
        
        # Parseamos y validamos
        analysis_data = DashboardAnalysisResult.parse_raw(analysis_json)
        
        print(f"[DashboardAnalyzer] Resumen de IA generado.")
        return analysis_data.dict()

    except Exception as e:
        print(f"Error al analizar las métricas del dashboard: {e}")
        # Devolver un resumen genérico si la IA falla
        return {
            "resumen_ia": "Aquí verás tu resumen emocional cuando escribas en tu diario.",
            "recomendacion_ia": "Intenta escribir cómo te sientes hoy para empezar.",
            "fuente_modelo": "fallback"
        }