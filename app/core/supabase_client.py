from datetime import datetime
from app.core.database import supabase  # Asegúrate de tener tu conexión global aquí


def guardar_entrada_diario(usuario_id: str, contenido: str, resumen: str, emocion: str, categoria: str, promedio_sentimiento: float):
    """
    Guarda una nueva entrada en la tabla 'entradas_diario' en Supabase.
    """
    try:
        response = supabase.table("entradas_diario").insert({
            "usuario_id": usuario_id,
            "contenido": contenido,
            "resumen": resumen,
            "emocion_predominante": emocion,
            "categoria_emocional": categoria,
            "promedio_sentimiento": promedio_sentimiento,
            "fecha": datetime.now().isoformat()
        }).execute()

        print(f"✅ Entrada guardada en Supabase: {response}")
        return response

    except Exception as e:
        print(f"❌ Error al guardar entrada: {e}")
        return None


def generar_metricas_emocionales(usuario_id: str):
    """
    Calcula y guarda un resumen emocional básico del usuario.
    (Versión simplificada para probar la integración)
    """
    try:
        # Traer todas las entradas del usuario
        data = supabase.table("entradas_diario").select("*").eq("usuario_id", usuario_id).execute()

        if not data.data:
            print("⚠️ No hay entradas para generar métricas.")
            return

        # Contar emociones
        conteo = {}
        for entrada in data.data:
            emocion = entrada["emocion_predominante"]
            conteo[emocion] = conteo.get(emocion, 0) + 1

        # Emoción más frecuente
        emocion_dominante = max(conteo, key=conteo.get)
        total = sum(conteo.values())
        proporciones = {k: v / total for k, v in conteo.items()}

        # Promedio de sentimiento
        promedio = sum(e["promedio_sentimiento"] for e in data.data) / total

        # Guardar métrica en Supabase
        response = supabase.table("metricas_emocionales").insert({
            "usuario_id": usuario_id,
            "emociones_predominantes": proporciones,
            "promedio_sentimiento": promedio,
            "periodo": datetime.now().strftime("%Y-%m-%d"),
            "resumen_periodo": f"Tu emoción más frecuente fue {emocion_dominante}.",
            "recomendacion_general": "Continúa registrando tus emociones para fortalecer tu autoconocimiento.",
            "actualizado_en": datetime.now().isoformat()
        }).execute()

        print(f"✅ Métricas generadas: {response}")
        return response

    except Exception as e:
        print(f"❌ Error al generar métricas: {e}")
        return None
