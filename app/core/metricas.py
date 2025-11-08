from app.core.supabase_client import supabase
from datetime import datetime
from collections import Counter
from statistics import mean

# ==========================================================
# 📈 MÉTRICAS EMOCIONALES - ANÁLISIS AGREGADO
# ==========================================================

def generar_metricas_emocionales(usuario_id: str):
    """
    Calcula las métricas emocionales del usuario basadas en sus mensajes.
    Guarda los resultados en la tabla 'metricas_emocionales'.
    """
    # 1️⃣ Obtener mensajes del usuario
    mensajes = supabase.table("mensajes_chat").select("categoria_emocional, puntuacion_sentimiento").eq("usuario_id", usuario_id).execute()

    if not mensajes.data:
        print("⚠️ No hay mensajes para calcular métricas.")
        return None

    categorias = [m["categoria_emocional"] for m in mensajes.data if m["categoria_emocional"]]
    puntajes = [float(m["puntuacion_sentimiento"]) for m in mensajes.data if m["puntuacion_sentimiento"] is not None]

    # 2️⃣ Calcular proporciones
    total = len(categorias)
    proporciones = dict(Counter(categorias))
    for k in proporciones:
        proporciones[k] = round(proporciones[k] / total, 2)

    # 3️⃣ Calcular promedio
    promedio_sentimiento = round(mean(puntajes), 2) if puntajes else 0.0

    # 4️⃣ Generar resumen textual
    resumen = f"Tu estado emocional promedio es {promedio_sentimiento}, con mayor presencia de: {max(proporciones, key=proporciones.get)}."

    # 5️⃣ Guardar en Supabase
    supabase.table("metricas_emocionales").insert({
        "usuario_id": usuario_id,
        "periodo": datetime.now().strftime("%Y-W%U"),
        "emociones_predominantes": proporciones,
        "promedio_sentimiento": promedio_sentimiento,
        "resumen_periodo": resumen,
        "recomendacion_general": "Sigue escribiendo cada día para fortalecer tu autoconocimiento emocional."
    }).execute()

    print("✅ Métricas emocionales actualizadas correctamente.")
    return resumen
