from pydantic import BaseModel
import os

class Settings(BaseModel):
    mongodb_url: str = os.getenv("MONGO_PUBLIC_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "todolist")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
