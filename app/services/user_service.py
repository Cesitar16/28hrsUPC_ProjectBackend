from app.core.database import supabase
from typing import Optional, Dict, Any

def crear_usuario(id_auth: str, email: str, nombre: Optional[str] = None) -> Dict[str, Any]:
    """
    Crea un nuevo usuario en nuestra tabla 'usuarios'.
    Este ID debe venir de Supabase Auth.
    """
    data = {
        "id": id_auth,  # Usamos el UUID de Supabase Auth
        "nombre": nombre,
        "email": email
    }
    try:
        res = supabase.table("usuarios").insert(data).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        # Manejar el caso de que el usuario ya exista (ej. Primary Key violation)
        print(f"Error al insertar en tabla 'usuarios': {e}")
        # Si ya existe, simplemente lo obtenemos
        return obtener_usuario_por_email(email)


def obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario existente por correo electrónico.
    (Esta función está perfecta como la tenías)
    """
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error al obtener usuario por email: {e}")
        return None
    
def obtener_usuario_por_id(usuario_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario existente por su UUID.
    """
    try:
        res = supabase.table("usuarios").select("*").eq("id", usuario_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error al obtener usuario por ID: {e}")
        return None