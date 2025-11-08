from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_routes, diario_routes, users_routes, dashboard_routes

app = FastAPI(
    title="MiDiarioAI API",
    description="API para la aplicación de bienestar emocional MiDiarioAI.",
    version="1.0.0"
)

origins = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_routes.router, prefix="/api")

app.include_router(chat_routes.router, prefix="/api")

app.include_router(diario_routes.router, prefix="/api")

app.include_router(dashboard_routes.router, prefix="/api")

@app.get("/")
def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"message": "Bienvenido a MiDiarioAI API. (v1.0.0)"}