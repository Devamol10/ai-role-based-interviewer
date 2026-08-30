import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ai-role-based-interviewer"
    API_V1_STR: str = "/api"
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interviewer.db")
    
    # RAG & LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
