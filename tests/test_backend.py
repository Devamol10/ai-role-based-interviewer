import sys
import io
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import inspect
import pymupdf as fitz

# Add backend directory to path so app imports resolve
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.database import engine, init_db, SessionLocal
from app.models.candidate import Candidate
from app.rag.chunker import chunk_text
from app.rag.ingestion import get_knowledge_base_dir

client = TestClient(app)

def create_sample_pdf_bytes(text: str = "John Doe\nSoftware Engineer\nSkills: Python, FastAPI") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def test_health_endpoint_status():
    response = client.get("/api/health")
    assert response.status_code == 200

def test_health_endpoint_response_body():
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-role-based-interviewer"

def test_database_initialization():
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = {
        "candidates",
        "interview_sessions",
        "interview_questions",
        "interview_answers",
        "interview_reports",
    }
    for table in expected_tables:
        assert table in tables

def test_upload_valid_resume_pdf():
    pdf_bytes = create_sample_pdf_bytes("Alice Smith\nBackend Engineer\nPython FastAPI SQLite")
    files = {
        "file": ("alice_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")
    }
    data = {"role": "Backend Engineer"}

    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["filename"] == "alice_resume.pdf"
    assert res_data["selected_role"] == "Backend Engineer"
    assert res_data["extracted_text_length"] > 0
    assert "candidate_id" in res_data

def test_chunker_splits_paragraphs_and_attaches_metadata():
    sample_text = (
        "Paragraph One introduces database indexes and B-Trees for rapid lookup performance.\n\n"
        "Paragraph Two discusses ACID transaction isolation levels including Read Committed and Serializable.\n\n"
        "Paragraph Three details sharding keys and horizontal partitioning across nodes."
    )
    chunks = chunk_text(sample_text, source="databases.md", role="backend_engineer", chunk_size=150, overlap=30)
    
    assert len(chunks) >= 2
    for idx, c in enumerate(chunks):
        assert "text" in c
        assert c["metadata"]["source"] == "databases.md"
        assert c["metadata"]["role"] == "backend_engineer"
        assert c["metadata"]["chunk_index"] == idx

def test_knowledge_base_directory_discovery():
    kb_dir = get_knowledge_base_dir()
    assert kb_dir.exists()
    assert (kb_dir / "backend_engineer").exists()
    assert (kb_dir / "ai_ml_engineer").exists()
    assert (kb_dir / "data_science").exists()

def test_rag_search_validation_empty_query():
    payload = {
        "query": "  ",
        "role": "Backend Engineer",
        "top_k": 5
    }
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 422

def test_rag_search_validation_unsupported_role():
    payload = {
        "query": "What is indexing?",
        "role": "Fullstack Developer",
        "top_k": 5
    }
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 422

@patch("app.rag.retrieval.generate_embeddings")
@patch("app.rag.retrieval.query_vector_store")
def test_rag_search_mocked_success(mock_query_vs, mock_gen_embeds):
    mock_gen_embeds.return_value = [[0.1, 0.2, 0.3]]
    mock_query_vs.return_value = [
        {
            "text": "Database indexing utilizes B-Trees.",
            "source": "databases.md",
            "role": "backend_engineer",
            "chunk_index": 0
        }
    ]

    payload = {
        "query": "How does indexing work?",
        "role": "Backend Engineer",
        "top_k": 3
    }
    response = client.post("/api/rag/search", json=payload)
    assert response.status_code == 200
    res_data = response.json()

    assert res_data["query"] == "How does indexing work?"
    assert res_data["role"] == "Backend Engineer"
    assert res_data["result_count"] == 1
    assert res_data["results"][0]["source"] == "databases.md"
