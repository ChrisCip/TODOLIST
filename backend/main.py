from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
from app.schemas import UserCreate, User, Token
from app.auth import get_password_hash, create_access_token
from app.database import Database
from datetime import datetime
from bson import ObjectId

load_dotenv()

app = FastAPI()

# Obtener la URL del frontend desde las variables de entorno
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://todolist-sepia-seven-38.vercel.app",  # Tu dominio de Vercel (sin /login)
        "http://localhost:5173",  # Para desarrollo local
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de prueba para el healthcheck
@app.get("/")
async def read_root():
    return {"status": "ok"}

@app.post("/auth/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    try:
        db = Database.get_db()
        
        # Create new user with hashed password
        hashed_password = get_password_hash(user.password)
        user_dict = user.model_dump(exclude={"password"})
        user_dict.update({
            "password": hashed_password,
            "_id": str(ObjectId()),
            "created_at": datetime.utcnow()
        })
        
        await db.users.insert_one(user_dict)
        
        created_user = {
            "_id": user_dict["_id"],
            "name": user_dict["name"],
            "email": user_dict["email"]
        }
            
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Importar el resto de las rutas
from app.main import app as app_router
app.include_router(app_router) 