from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    id: UUID
    nombre: Optional[str] = None
    email: EmailStr
    creado_en: datetime


class MePatch(BaseModel):
    nombre: Optional[str] = None
