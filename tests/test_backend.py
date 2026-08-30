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
from app.models.answer import InterviewAnswer

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_submit_answer_session_not_found():
    payload = {"question_id": 1, "answer_text": "Valid test answer text"}
    response = client.post("/api/interview/99999/answer", json=payload)
    assert response.status_code == 404

def test_submit_answer_empty_rejected():
    payload = {"question_id": 1, "answer_text": "   "}
    response = client.post("/api/interview/1/answer", json=payload)
    assert response.status_code == 422

def test_submit_answer_question_not_found():
    db = SessionLocal()
    cand = Candidate(resume_filename="r.pdf", resume_text="txt", selected_role="Backend Engineer")
    db.add(cand)
    db.commit()
    session = InterviewSession(candidate_id=cand.id, status="active", current_question_number=1, total_questions=5)
    db.add(session)
    db.commit()
    s_id = session.id
    db.close()

    payload = {"question_id": 99999, "answer_text": "Valid answer text"}
    response = client.post(f"/api/interview/{s_id}/answer", json=payload)
    assert response.status_code == 404

@patch("app.services.interview_service.generate_interview_question")
@patch("app.services.interview_service.select_interview_topics")
def test_full_5_question_interview_flow(mock_topics, mock_question_gen):
    mock_topics.return_value = ["Topic A", "Topic B", "Topic C", "Topic D", "Topic E"]
    mock_question_gen.side_effect = lambda candidate_profile, role, topic, past_questions_context=None: {
        "question": f"Question about {topic}?",
        "topic": topic,
        "difficulty": "Medium",
        "reason": f"Testing {topic}",
        "retrieved_context": []
    }

    # 1. Setup Candidate and Session with Question 1
    db = SessionLocal()
    cand = Candidate(resume_filename="c.pdf", resume_text="Python FastAPI", selected_role="Backend Engineer")
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

    # 2. Answer Question 1 -> Advances to Question 2
    res1 = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q1_id, "answer_text": "Answer 1 text"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["next_question_number"] == 2
    assert data1["interview_completed"] is False
    assert data1["next_question"]["question_number"] == 2
    q2_id = data1["next_question"]["id"]

    # Test Duplicate Answer Rejection
    res_dup = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q1_id, "answer_text": "Duplicate answer"})
    assert res_dup.status_code == 400
    assert "already been submitted" in res_dup.json()["detail"]

    # 3. Answer Question 2 -> Question 3
    res2 = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q2_id, "answer_text": "Answer 2 text"})
    q3_id = res2.json()["next_question"]["id"]

    # 4. Answer Question 3 -> Question 4
    res3 = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q3_id, "answer_text": "Answer 3 text"})
    q4_id = res3.json()["next_question"]["id"]

    # 5. Answer Question 4 -> Question 5
    res4 = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q4_id, "answer_text": "Answer 4 text"})
    q5_id = res4.json()["next_question"]["id"]

    # 6. Answer Question 5 -> Complete Interview
    res5 = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q5_id, "answer_text": "Answer 5 text"})
    data5 = res5.json()
    assert data5["interview_completed"] is True
    assert data5["next_question_number"] is None
    assert data5["next_question"] is None

    # 7. Verify session DB status completed & exactly 5 questions created (no Q6)
    db = SessionLocal()
    sess_db = db.query(InterviewSession).filter(InterviewSession.id == s_id).first()
    assert sess_db.status == "completed"
    assert sess_db.completed_at is not None

    all_qs = db.query(InterviewQuestion).filter(InterviewQuestion.session_id == s_id).all()
    assert len(all_qs) == 5
    db.close()

def test_get_interview_and_questions_endpoints():
    db = SessionLocal()
    cand = Candidate(resume_filename="x.pdf", resume_text="txt", selected_role="Backend Engineer")
    db.add(cand)
    db.commit()
    session = InterviewSession(candidate_id=cand.id, status="active", current_question_number=1, total_questions=5)
    db.add(session)
    db.commit()

    q = InterviewQuestion(session_id=session.id, question_number=1, question_text="What is DB indexing?", topic="Database Performance")
    db.add(q)
    db.commit()
    s_id = session.id
    db.close()

    # GET /api/interview/{session_id}
    res_sess = client.get(f"/api/interview/{s_id}")
    assert res_sess.status_code == 200
    assert res_sess.json()["session_id"] == s_id
    assert res_sess.json()["current_question_number"] == 1

    # GET /api/interview/{session_id}/questions
    res_qs = client.get(f"/api/interview/{s_id}/questions")
    assert res_qs.status_code == 200
    assert res_qs.json()["total_questions"] == 1
    assert res_qs.json()["questions"][0]["question_text"] == "What is DB indexing?"
