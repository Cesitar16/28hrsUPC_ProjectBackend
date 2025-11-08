from fastapi import FastAPI
from app.routes.chat_routes import router as chat_router
from app.routes.diario_routes import router as diario_router
from fastapi.middleware.cors import CORSMiddleware
# ==========================================================
# 🧠 MI DIARIO IA - BACKEND PRINCIPAL
# ==========================================================

app = FastAPI(
    title="MiDiarioIA Backend",
    description="API del diario emocional inteligente 'Auri', basada en FastAPI + Supabase + OpenAI.",
    version="1.0.0",
)

# Rutas principales
app.include_router(chat_router)
app.include_router(diario_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta raíz
@app.get("/")
def root():
    return {"message": "🚀 API de MiDiarioIA lista y funcionando correctamente"}
