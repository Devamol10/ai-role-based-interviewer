import os
import hashlib
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.rag.config import rag_config

def get_chroma_client():
    os.makedirs(rag_config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    return chromadb.PersistentClient(path=rag_config.CHROMA_PERSIST_DIRECTORY)

def get_or_create_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=rag_config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def generate_chunk_id(role: str, source: str, chunk_index: int) -> str:
    raw_str = f"{role}:{source}:{chunk_index}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]

def upsert_chunks(chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
    if not chunks or not embeddings or len(chunks) != len(embeddings):
        return 0

    collection = get_or_create_collection()

    ids = []
    documents = []
    metadatas = []
    embeds = []

    for item, embed in zip(chunks, embeddings):
        meta = item["metadata"]
        doc_id = generate_chunk_id(meta["role"], meta["source"], meta["chunk_index"])
        
        ids.append(doc_id)
        documents.append(item["text"])
        metadatas.append(meta)
        embeds.append(embed)

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeds
    )

    return len(ids)

def query_vector_store(
    query_embedding: List[float],
    role: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    collection = get_or_create_collection()
    
    where_clause = {"role": role} if role else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )

    formatted_results = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        
        for doc, meta in zip(docs, metas):
            formatted_results.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "role": meta.get("role", "unknown"),
                "chunk_index": meta.get("chunk_index", 0)
            })

    return formatted_results
