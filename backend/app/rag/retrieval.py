from typing import List, Dict, Any
from app.rag.config import rag_config
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import query_vector_store

def retrieve_relevant_chunks(
    query: str,
    role: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    if not query or not query.strip():
        return []

    # Map human-readable UI role to internal folder name if needed
    mapped_role = rag_config.ROLE_MAPPING.get(role, role)

    # Generate query embedding
    query_embeddings = generate_embeddings([query.strip()])
    if not query_embeddings:
        return []

    query_vector = query_embeddings[0]

    # Query ChromaDB collection with role filter
    return query_vector_store(
        query_embedding=query_vector,
        role=mapped_role,
        top_k=top_k
    )
