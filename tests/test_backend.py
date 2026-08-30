import sys
import io
import json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import inspect
import pymupdf as fitz

backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.database import engine, init_db, SessionLocal
from app.models.candidate import Candidate
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion
from app.models.answer import InterviewAnswer
from app.models.report import InterviewReport
from app.rag.chunker import chunk_text
from app.rag.ingestion import get_knowledge_base_dir
from app.services.report_service import get_recommendation_label

client = TestClient(app)

def create_sample_pdf_bytes(text: str = "John Doe\nSoftware Engineer\nSkills: Python, FastAPI") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

# --- 1. Health Endpoint Tests ---
def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ai-role-based-interviewer"

# --- 2. Database Initialization Test ---
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

# --- 3. Resume Upload & Validation Tests ---
def test_upload_valid_resume_pdf():
    pdf_bytes = create_sample_pdf_bytes("Alice Smith\nBackend Engineer\nPython FastAPI SQLite")
    files = {"file": ("alice_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    data = {"role": "Backend Engineer"}

    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["filename"] == "alice_resume.pdf"
    assert res_data["selected_role"] == "Backend Engineer"
    assert res_data["extracted_text_length"] > 0
    assert "candidate_id" in res_data

def test_upload_invalid_file_type():
    files = {"file": ("resume.txt", io.BytesIO(b"Plain text content"), "text/plain")}
    data = {"role": "Backend Engineer"}
    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid file format" in response.json()["detail"]

def test_upload_missing_role():
    pdf_bytes = create_sample_pdf_bytes()
    files = {"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    data = {"role": ""}
    response = client.post("/api/resume/upload", files=files, data=data)
    assert response.status_code in (400, 422)

# --- 4. RAG Chunker & KB Discovery Tests ---
def test_chunker_splits_paragraphs_and_attaches_metadata():
    sample_text = (
        "Paragraph One introduces database indexes and B-Trees for rapid lookup performance.\n\n"
        "Paragraph Two discusses ACID transaction isolation levels including Read Committed and Serializable."
    )
    chunks = chunk_text(sample_text, source="databases.md", role="backend_engineer", chunk_size=150, overlap=30)
    assert len(chunks) >= 2
    for idx, c in enumerate(chunks):
        assert c["metadata"]["source"] == "databases.md"
        assert c["metadata"]["role"] == "backend_engineer"

def test_knowledge_base_directory_discovery():
    kb_dir = get_knowledge_base_dir()
    assert kb_dir.exists()
    assert (kb_dir / "backend_engineer").exists()
    assert (kb_dir / "ai_ml_engineer").exists()
    assert (kb_dir / "data_science").exists()

def test_rag_search_validation():
    # Empty query
    res1 = client.post("/api/rag/search", json={"query": "  ", "role": "Backend Engineer", "top_k": 5})
    assert res1.status_code == 422
    # Unsupported role
    res2 = client.post("/api/rag/search", json={"query": "Indexing", "role": "DevOps Engineer", "top_k": 5})
    assert res2.status_code == 422

@patch("app.rag.retrieval.generate_embeddings")
@patch("app.rag.retrieval.query_vector_store")
def test_rag_search_mocked_success(mock_query_vs, mock_gen_embeds):
    mock_gen_embeds.return_value = [[0.1, 0.2, 0.3]]
    mock_query_vs.return_value = [
        {"text": "Database indexing uses B-Trees.", "source": "databases.md", "role": "backend_engineer", "chunk_index": 0}
    ]
    response = client.post("/api/rag/search", json={"query": "Indexing", "role": "Backend Engineer", "top_k": 3})
    assert response.status_code == 200
    assert response.json()["result_count"] == 1

# --- 5. Interactive Interview & Question Generation Tests ---
def test_question_generate_candidate_not_found():
    response = client.post("/api/interview/questions/generate", json={"candidate_id": 99999})
    assert response.status_code == 404

def test_submit_answer_validation():
    # Empty answer
    res1 = client.post("/api/interview/1/answer", json={"question_id": 1, "answer_text": "   "})
    assert res1.status_code == 422
    # Non-existent session
    res2 = client.post("/api/interview/99999/answer", json={"question_id": 1, "answer_text": "Valid text answer"})
    assert res2.status_code == 404

def test_recommendation_thresholds():
    assert get_recommendation_label(9.2) == "Strong Candidate"
    assert get_recommendation_label(7.8) == "Good Candidate"
    assert get_recommendation_label(6.2) == "Needs Improvement"
    assert get_recommendation_label(4.5) == "Significant Gaps"

def test_report_generation_incomplete_session_rejected():
    db = SessionLocal()
    cand = Candidate(resume_filename="r.pdf", resume_text="txt", selected_role="Backend Engineer")
    db.add(cand)
    db.commit()
    session = InterviewSession(candidate_id=cand.id, status="active", current_question_number=1, total_questions=5)
    db.add(session)
    db.commit()
    s_id = session.id
    db.close()

    response = client.get(f"/api/interview/{s_id}/report")
    assert response.status_code == 400

@patch("app.services.interview_service.generate_interview_question")
@patch("app.services.interview_service.select_interview_topics")
@patch("app.services.interview_service.evaluate_answer")
@patch("app.api.routes.reports.generate_summary")
def test_full_5_question_flow_and_report(mock_summary, mock_eval, mock_topics, mock_qgen):
    mock_topics.return_value = ["Topic A", "Topic B", "Topic C", "Topic D", "Topic E"]
    mock_qgen.side_effect = lambda candidate_profile, role, topic, past_questions_context=None: {
        "question": f"Question regarding {topic}?",
        "topic": topic,
        "difficulty": "Medium",
        "reason": f"Testing {topic}",
        "retrieved_context": []
    }
    mock_eval.side_effect = lambda question_text, answer_text, role, topic, retrieved_context: {
        "score": 8.0,
        "feedback": "Solid answer.",
        "strengths": ["Good concept"],
        "improvements": ["Minor detail"]
    }
    mock_summary.return_value = "Candidate performed well across all 5 technical topics."

    # Step A: Setup Candidate and active Session with Q1
    db = SessionLocal()
    cand = Candidate(resume_filename="c.pdf", resume_text="FastAPI Python", selected_role="Backend Engineer")
    db.add(cand)
    db.commit()
    session = InterviewSession(candidate_id=cand.id, status="active", current_question_number=1, total_questions=5)
    db.add(session)
    db.commit()
    q1 = InterviewQuestion(session_id=session.id, question_number=1, question_text="Q1 text", topic="Topic A", difficulty="Medium")
    db.add(q1)
    db.commit()
    s_id = session.id
    q1_id = q1.id
    db.close()

    # Step B: Progress through Questions 1 to 5
    curr_q_id = q1_id
    for q_num in range(1, 6):
        res = client.post(f"/api/interview/{s_id}/answer", json={"question_id": curr_q_id, "answer_text": f"Substantive answer for Question {q_num}"})
        assert res.status_code == 200
        res_data = res.json()
        if q_num < 5:
            assert res_data["interview_completed"] is False
            assert res_data["next_question_number"] == q_num + 1
            curr_q_id = res_data["next_question"]["id"]
        else:
            assert res_data["interview_completed"] is True
            assert res_data["next_question_number"] is None

    # Step C: Verify Session state Completed & no Q6
    db = SessionLocal()
    sess_db = db.query(InterviewSession).filter(InterviewSession.id == s_id).first()
    assert sess_db.status == "completed"
    assert sess_db.completed_at is not None
    all_qs = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == s_id).all()
    assert len(all_qs) == 5
    db.close()

    # Step D: Verify Report endpoint
    res_rep = client.get(f"/api/interview/{s_id}/report")
    assert res_rep.status_code == 200
    rep = res_rep.json()
    assert rep["session_id"] == s_id
    assert rep["overall_score"] > 0.0
    assert rep["recommendation"] in ["Strong Candidate", "Good Candidate"]

    # Step E: Verify Questions endpoint returns full scores & feedback
    res_qs = client.get(f"/api/interview/{s_id}/questions")
    assert res_qs.status_code == 200
    assert len(res_qs.json()["questions"]) == 5
    assert res_qs.json()["questions"][0]["score"] == 8.0
