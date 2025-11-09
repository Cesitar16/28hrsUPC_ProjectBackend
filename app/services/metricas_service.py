from app.core.database import supabase
from datetime import datetime
from typing import Optional, Dict, Any, List

def calcular_metricas_dashboard(usuario_id: str) -> Dict[str, Any]:
    """
    Calcula y devuelve las métricas agregadas para el dashboard del usuario.
    """
    try:
        print(f"[DashboardService] Calculando métricas para {usuario_id}")
        
        entradas_res = supabase.table("entradas_diario") \
            .select("emocion_predominante, categoria_emocional, promedio_sentimiento") \
            .eq("usuario_id", usuario_id) \
            .execute()
        
        entradas = entradas_res.data or []

        mensajes_res = supabase.table("mensajes_chat") \
            .select("emocion_detectada, categoria_emocional, puntuacion_sentimiento") \
            .eq("usuario_id", usuario_id) \
            .eq("rol", "user") \
            .filter("emocion_detectada", "not.is", "null") \
            .execute()
            
        mensajes = mensajes_res.data or []

        total_entradas = len(entradas)
        total_mensajes_analizados = len(mensajes)

        conteo_emociones = {}
        total_sentimiento = 0.0
        conteo_total = 0

        # Iteramos sobre las entradas del diario
        for entrada in entradas:
            emocion = entrada.get('emocion_predominante')
            sentimiento = entrada.get('promedio_sentimiento')
            if emocion:
                emocion = emocion.lower() # Normalizamos
                conteo_emociones[emocion] = conteo_emociones.get(emocion, 0) + 1
            if sentimiento is not None:
                total_sentimiento += sentimiento
                conteo_total += 1

        # Iteramos sobre los mensajes de chat analizados
        for mensaje in mensajes:
            emocion = mensaje.get('emocion_detectada')
            sentimiento = mensaje.get('puntuacion_sentimiento')
            if emocion:
                emocion = emocion.lower() # Normalizamos
                conteo_emociones[emocion] = conteo_emociones.get(emocion, 0) + 1
            if sentimiento is not None:
                total_sentimiento += sentimiento
                conteo_total += 1

        promedio_sentimiento_general = (total_sentimiento / conteo_total) if conteo_total > 0 else 0.0

        emocion_principal = None
        if conteo_emociones:
            emocion_principal = max(conteo_emociones, key=conteo_emociones.get)

        # 4. Devolver el resultado
        return {
            "total_entradas_diario": total_entradas,
            "emocion_mas_frecuente": emocion_principal,
            "conteo_emociones": conteo_emociones,
            "promedio_sentimiento_general": round(promedio_sentimiento_general, 2)
        }

    except Exception as e:
        print(f"Error al calcular métricas del dashboard: {e}")
        return {"error": str(e)}