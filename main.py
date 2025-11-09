from __future__ import annotations

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth import AuthMiddleware, get_token_verifier
from app.core.settings import get_settings
from app.routes import auth as auth_routes
from app.routes import chat as chat_routes
from app.routes import consejos as consejos_routes
from app.routes import diario as diario_routes
from app.routes import feedback as feedback_routes
from app.routes import health as health_routes
from app.routes import metricas as metricas_routes
from app.routes import progreso as progreso_routes

settings = get_settings()

app = FastAPI(
    title="MiDiarioIA API",
    description="Backend para la aplicación de bienestar emocional MiDiarioIA.",
    version="1.0.0",
)

app.state.start_time = time.time()
app.state.settings = settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware, verifier=get_token_verifier(settings))

app.include_router(health_routes.router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(diario_routes.router, prefix="/api/v1")
app.include_router(chat_routes.router, prefix="/api/v1")
app.include_router(feedback_routes.router, prefix="/api/v1")
app.include_router(metricas_routes.router, prefix="/api/v1")
app.include_router(consejos_routes.router, prefix="/api/v1")
app.include_router(progreso_routes.router, prefix="/api/v1")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "MiDiarioIA API - refer to /api/v1/health for status"}
