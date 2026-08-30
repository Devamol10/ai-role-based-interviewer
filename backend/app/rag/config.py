from app.core.config import settings

class RAGConfig:
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    EMBEDDING_MODEL: str = settings.OPENAI_EMBEDDING_MODEL
    CHROMA_PERSIST_DIRECTORY: str = settings.CHROMA_PERSIST_DIRECTORY
    COLLECTION_NAME: str = "role_knowledge"

    # Mapping human-readable roles from UI to internal directory names
    ROLE_MAPPING: dict[str, str] = {
        "Backend Engineer": "backend_engineer",
        "AI/ML Engineer": "ai_ml_engineer",
        "Data Science / Applied ML": "data_science"
    }

rag_config = RAGConfig()
