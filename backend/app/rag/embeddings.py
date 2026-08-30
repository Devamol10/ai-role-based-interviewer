from typing import List
from openai import OpenAI
from fastapi import HTTPException, status

from app.core.config import settings

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates vector embeddings for a list of text strings using OpenAI API with fallback for missing key.
    """
    if not texts:
        return []

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        # Return deterministic mock embeddings vector (1536 dimension zeros/floats) for offline demo
        import hashlib
        result = []
        for text in texts:
            # Deterministic pseudo-embedding from text hash
            h = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
            dummy_vec = [((h + i) % 100) / 100.0 for i in range(1536)]
            result.append(dummy_vec)
        return result

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.embeddings.create(
            input=texts,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )
