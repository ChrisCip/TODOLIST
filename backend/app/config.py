from pydantic import BaseModel
import os

class Settings(BaseModel):
    mongodb_url: str = "mongodb+srv://todolistuser:4mpxFHXMr9zdXejj@cluster0.qzj74.mongodb.net/todolist?retryWrites=true&w=majority&appName=Cluster0"  # Get from env var
    database_name: str = "todolist"
    secret_key: str = "your-secret-key-here"  # Change this in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = True  # Set to False in production

    class Config:
        env_file = ".env"

settings = Settings()
