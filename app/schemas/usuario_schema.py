from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

# SCHEMAS - USUARIOS Y AUTENTICACIÓN

class UsuarioCreate(BaseModel):
    """
    Schema para registrar un nuevo usuario.
    """
    email: EmailStr
    password: str = Field(..., min_length=6)
    nombre: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "password123",
                "nombre": "Ana"
            }
        }

class UsuarioLogin(BaseModel):
    """
    Schema para iniciar sesión.
    """
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "password123"
            }
        }

class TokenResponse(BaseModel):
    """
    Schema para devolver la respuesta de Supabase (token, etc.)
    """
    access_token: str
    token_type: str = "bearer"