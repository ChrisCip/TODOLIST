from pydantic import BaseModel

class Settings(BaseModel):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "todolist"
    secret_key: str = "your-secret-key-here"  # Change this in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = True  # Set to False in production

    class Config:
        env_file = ".env"

settings = Settings()
