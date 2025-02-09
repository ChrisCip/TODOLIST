from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Obtener la URL del frontend desde las variables de entorno
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "https://todolist-sepia-seven-38.vercel.app",  # Tu dominio de Vercel
        "http://localhost:5173",  # Para desarrollo local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de prueba para el healthcheck
@app.get("/")
async def read_root():
    return {"status": "ok"}

# ... resto de tus rutas 