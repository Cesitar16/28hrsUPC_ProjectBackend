from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.supabase_client import supabase
from gotrue.errors import AuthApiError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependencia de FastAPI para obtener el usuario autenticado
    a partir del token JWT de Supabase.
    """
    try:
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_response.user.id
    
    except AuthApiError as e:
        print(f"Error de GoTrue al validar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {e.message}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error inesperado en get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al validar la sesión."
        )

AuthUser = Depends(get_current_user)