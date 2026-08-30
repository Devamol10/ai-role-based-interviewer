import sys
import io
import json
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
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion

client = TestClient(app)

def create_sample_pdf_bytes(text: str = "John Doe\nSoftware Engineer\nSkills: Python, FastAPI") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_question_generate_candidate_not_found():
    payload = {"candidate_id": 99999}
    response = client.post("/api/interview/questions/generate", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_question_generate_invalid_candidate_id():
    payload = {"candidate_id": -1}
    response = client.post("/api/interview/questions/generate", json=payload)
    assert response.status_code == 422

@patch("app.api.routes.questions.generate_interview_question")
@patch("app.api.routes.questions.select_interview_topics")
@patch("app.api.routes.questions.extract_candidate_profile")
def test_question_generate_success_and_persistence(mock_profile, mock_topics, mock_question_gen):
    # 1. Create candidate in DB
    db = SessionLocal()
    cand = Candidate(
        resume_filename="test_resume.pdf",
        resume_text="Experienced Python FastAPI developer",
        selected_role="Backend Engineer",
        extracted_skills=["Python", "FastAPI"],
        extracted_technologies=["PostgreSQL", "Docker"]
    )
    db.add(cand)
    db.commit()
    db.refresh(cand)
    cand_id = cand.id
    db.close()

    # Mocks
    mock_profile.return_value = {
        "skills": ["Python", "FastAPI"],
        "technologies": ["PostgreSQL", "Docker"],
        "experience_summary": "Factual test summary"
    }
    mock_topics.return_value = ["Database Performance", "API Design"]
    mock_question_gen.return_value = {
        "question": "How do you optimize PostgreSQL queries in FastAPI?",
        "topic": "Database Performance",
        "difficulty": "Medium",
        "reason": "Tailored to candidate's PostgreSQL experience.",
        "retrieved_context": [
            {
                "text": "Database indexing optimizes lookup queries.",
                "source": "databases.md",
                "role": "backend_engineer",
                "chunk_index": 0
            }
        ]
    }

    # 2. Call API
    payload = {"candidate_id": cand_id}
    response = client.post("/api/interview/questions/generate", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["question_text"] == "How do you optimize PostgreSQL queries in FastAPI?"
    assert data["topic"] == "Database Performance"
    assert data["difficulty"] == "Medium"
    assert len(data["retrieved_context"]) == 1

    # 3. Verify SQLite DB records (Session & Question)
    db = SessionLocal()
    session = db.query(InterviewSession).filter(InterviewSession.candidate_id == cand_id).first()
    assert session is not None
    assert session.status == "active"
    assert session.current_question_number == 1

    question = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session.id).first()
    assert question is not None
    assert question.question_text == "How do you optimize PostgreSQL queries in FastAPI?"
    assert question.topic == "Database Performance"
    assert "databases.md" in question.retrieved_context
    db.close()
