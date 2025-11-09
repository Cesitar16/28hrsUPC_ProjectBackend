from fastapi import APIRouter, HTTPException, Body
from app.core.supabase_client import supabase
from app.schemas.usuario_schema import UsuarioCreate, UsuarioLogin, TokenResponse
import app.services.user_service as user_service
from gotrue.errors import AuthApiError

router = APIRouter()

# ENDPOINTS - AUTENTICACIÓN Y USUARIOS
@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Registrar un nuevo usuario",
    tags=["Autenticación"]
)
def register_user(
    usuario_in: UsuarioCreate = Body(...)
):
    """
    Registra un nuevo usuario en Supabase Auth.
    
    Además, guarda el 'nombre' (si se provee) en nuestra tabla 'usuarios'
    pública usando el user_service.
    """
    try:
        auth_response = supabase.auth.sign_up({
            "email": usuario_in.email,
            "password": usuario_in.password,
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(status_code=400, detail="No se pudo registrar al usuario. El email podría estar en uso.")

        print(f"Nuevo usuario registrado en Auth: {auth_response.user.id}")

        user_service.crear_usuario(
            id_auth=auth_response.user.id,
            email=usuario_in.email,
            nombre=usuario_in.nombre
        )
        
        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer"
        }

    except AuthApiError as e:
        print(f"Error de Supabase al registrar: {e}")
        raise HTTPException(status_code=400, detail=f"Error al registrar: {e.message}")
    except Exception as e:
        print(f"Error inesperado en /register: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Iniciar sesión (Obtener Token)",
    tags=["Autenticación"]
)
def login_for_access_token(
    form_data: UsuarioLogin = Body(...)
):
    """
    Inicia sesión con email y contraseña y devuelve un Access Token.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.email,
            "password": form_data.password
        })

        if not auth_response.session or not auth_response.session.access_token:
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos.")

        print(f"Usuario {form_data.email} ha iniciado sesión.")

        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer"
        }
        
    except AuthApiError as e:
        print(f"Error de Supabase al iniciar sesión: {e}")
        raise HTTPException(status_code=401, detail=f"Email o contraseña incorrectos: {e.message}")
    except Exception as e:
        print(f"Error inesperado en /token: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")