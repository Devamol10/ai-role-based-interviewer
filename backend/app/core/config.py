import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ai-role-based-interviewer"
    API_V1_STR: str = "/api"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interviewer.db")
    
    class Config:
        case_sensitive = True

settings = Settings()
