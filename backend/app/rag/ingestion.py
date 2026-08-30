import os
from pathlib import Path
from typing import Dict, Any

from app.rag.chunker import chunk_text
from app.rag.embeddings import generate_embeddings
from app.rag.vector_store import upsert_chunks

def get_knowledge_base_dir() -> Path:
    # Locate root knowledge_base folder relative to backend directory
    backend_dir = Path(__file__).resolve().parent.parent.parent
    return backend_dir.parent / "knowledge_base"

def ingest_knowledge_base() -> Dict[str, Any]:
    kb_dir = get_knowledge_base_dir()
    if not kb_dir.exists():
        return {"status": "error", "message": f"Knowledge base directory {kb_dir} does not exist."}

    total_files = 0
    total_chunks = 0
    roles_processed = {}

    # Iterate over role subdirectories
    for role_dir in kb_dir.iterdir():
        if role_dir.is_dir():
            role_name = role_dir.name
            role_files = 0
            role_chunks_count = 0

            for file_path in role_dir.glob("*"):
                if file_path.suffix.lower() in [".txt", ".md"] and file_path.name != "README.md":
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        chunks = chunk_text(
                            text=content,
                            source=file_path.name,
                            role=role_name
                        )
                        if chunks:
                            texts = [c["text"] for c in chunks]
                            embeddings = generate_embeddings(texts)
                            stored_count = upsert_chunks(chunks, embeddings)

                            role_files += 1
                            role_chunks_count += stored_count
                    except Exception as err:
                        print(f"Error processing {file_path}: {err}")

            if role_files > 0:
                roles_processed[role_name] = {
                    "documents": role_files,
                    "chunks": role_chunks_count
                }
                total_files += role_files
                total_chunks += role_chunks_count

    return {
        "status": "success",
        "total_documents": total_files,
        "total_chunks": total_chunks,
        "roles": roles_processed
    }
