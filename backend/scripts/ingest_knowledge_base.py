import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.rag.ingestion import ingest_knowledge_base

def main():
    print("=== Starting Knowledge Base Ingestion ===")
    result = ingest_knowledge_base()
    
    if result.get("status") == "success":
        print("\nKnowledge Base Ingestion Complete!")
        print(f"Total Documents: {result['total_documents']}")
        print(f"Total Chunks: {result['total_chunks']}\n")
        print("Role breakdown:")
        for role, stats in result.get("roles", {}).items():
            print(f"  - {role}: {stats['documents']} docs, {stats['chunks']} chunks")
    else:
        print(f"Ingestion failed: {result.get('message')}")

if __name__ == "__main__":
    main()
