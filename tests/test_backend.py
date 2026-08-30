import sys
import io
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import inspect
import pymupdf as fitz

# Add backend directory to path so app imports resolve
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.database import engine, init_db, SessionLocal
from app.models.candidate import Candidate

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

    # Verify DB persistence
    db = SessionLocal()
    candidate = db.query(Candidate).filter(Candidate.id == res_data["candidate_id"]).first()
    assert candidate is not None
    assert candidate.resume_filename == "alice_resume.pdf"
    assert "Alice Smith" in candidate.resume_text
    assert candidate.selected_role == "Backend Engineer"
    db.close()

def test_upload_missing_file():
    data = {"role": "Backend Engineer"}
    response = client.post("/api/resume/upload", data=data)
    assert response.status_code == 422  # Unprocessable Entity for missing required form file

def test_upload_invalid_file_type():
    files = {
        "file": ("resume.txt", io.BytesIO(b"Plain text content"), "text/plain")
    }
    data = {"role": "Backend Engineer"}
    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_upload_missing_role():
    pdf_bytes = create_sample_pdf_bytes()
    files = {
        "file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")
    }
    data = {"role": ""}
    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code in (400, 422)
