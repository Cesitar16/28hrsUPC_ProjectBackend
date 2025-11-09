from app.core.database import supabase
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.analysis.diary_analyzer import analyze_diary_content



# 📓 ENTRADAS DE DIARIO (VERSIÓN MEJORADA)
def crear_entrada_diario(
    usuario_id: str,
    contenido: str,
    titulo: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Guarda una entrada de diario y luego la enriquece con análisis de IA.
    Este es el flujo de "Insertar -> Analizar -> Actualizar".
    """
    try:
        # 1. INSERTAR (Guardar la entrada inicial del usuario)
        print(f"[DiarioService] Guardando entrada inicial para usuario {usuario_id}")
        fecha_actual = datetime.now().date().isoformat()
        
        insert_data = {
            "usuario_id": usuario_id,
            "titulo": titulo,
            "contenido": contenido,
            "fecha": fecha_actual
            # Los campos de IA (resumen_ia, emocion, etc.) se dejan en NULL
        }
        
        # Usamos .execute() para obtener los datos insertados, incluido el ID
        insert_res = supabase.table("entradas_diario").insert(insert_data).execute()
        
        if not insert_res.data:
            print("[DiarioService] Error: No se pudo insertar la entrada inicial en Supabase.")
            return None

        # Obtenemos el ID de la entrada recién creada
        nueva_entrada = insert_res.data[0]
        id_entrada = nueva_entrada.get("id")
        
        if not id_entrada:
            print("[DiarioService] Error: No se pudo obtener el ID de la nueva entrada.")
            return None
            
        print(f"[DiarioService] Entrada inicial guardada con ID: {id_entrada}")

       
        # 2. ANALIZAR (Llamar al módulo de IA)
       
        print(f"[DiarioService] Iniciando análisis de IA para la entrada {id_entrada}...")
        analysis_results = analyze_diary_content(contenido)
        
        if not analysis_results:
            print(f"[DiarioService] Error: El análisis de IA falló. La entrada {id_entrada} queda sin análisis.")
            # Devolvemos la entrada sin enriquecer, es mejor que nada.
            return nueva_entrada

       
        # 3. ACTUALIZAR (Enriquecer la entrada con los resultados de la IA)
       
        print(f"[DiarioService] Actualizando entrada {id_entrada} con análisis de IA...")
        
        # El diccionario 'analysis_results' ya tiene los nombres de campo
        # correctos: resumen_ia, emocion_predominante, etc.
        
        update_res = supabase.table("entradas_diario") \
            .update(analysis_results) \
            .eq("id", id_entrada) \
            .execute()

        if not update_res.data:
            print(f"[DiarioService] Error: No se pudo actualizar la entrada {id_entrada} con el análisis.")
            # Devolvemos la entrada original si la actualización falla
            return nueva_entrada
            
        print(f"[DiarioService] Entrada {id_entrada} enriquecida exitosamente.")
        
        # Devolvemos la entrada completada y enriquecida
        return update_res.data[0]

    except Exception as e:
        print(f"Error catastrófico en crear_entrada_diario: {e}")
        return None


def obtener_entradas_diario(usuario_id: str) -> List[Dict[str, Any]]:
    """
    Devuelve todas las entradas del diario de un usuario.
    (Esta función permanece igual que en el Paso 1)
    """
    try:
        res = supabase.table("entradas_diario").select("*").eq("usuario_id", usuario_id).order("fecha", desc=True).execute()
        return res.data or []
    except Exception as e:
        print(f"Error al obtener entradas de diario: {e}")
        return []