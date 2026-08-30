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
from app.models.report import InterviewReport
from app.services.report_service import get_recommendation_label

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200

def test_recommendation_thresholds():
    assert get_recommendation_label(9.2) == "Strong Candidate"
    assert get_recommendation_label(8.5) == "Strong Candidate"
    assert get_recommendation_label(7.8) == "Good Candidate"
    assert get_recommendation_label(7.0) == "Good Candidate"
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
    assert "not completed" in response.json()["detail"].lower()

@patch("app.services.interview_service.generate_interview_question")
@patch("app.services.interview_service.select_interview_topics")
@patch("app.services.interview_service.evaluate_answer")
@patch("app.api.routes.reports.generate_summary")
def test_answer_evaluation_and_final_report(mock_gen_summary, mock_eval_answer, mock_topics, mock_qgen):
    mock_topics.return_value = ["Topic A", "Topic B"]
    mock_qgen.return_value = {
        "question": "Next question?",
        "topic": "Topic B",
        "difficulty": "Medium",
        "reason": "Reason",
        "retrieved_context": []
    }
    mock_eval_answer.side_effect = lambda question_text, answer_text, role, topic, retrieved_context: {
        "score": 8.0,
        "feedback": "Great technical answer.",
        "strengths": ["Clear concept"],
        "improvements": ["Minor detail missing"]
    }
    mock_gen_summary.return_value = "Candidate demonstrated strong engineering capabilities across all topics."

    # Setup Candidate and completed Session with 5 questions & answers
    db = SessionLocal()
    cand = Candidate(resume_filename="c.pdf", resume_text="txt", selected_role="Backend Engineer")
    db.add(cand)
    db.commit()

    session = InterviewSession(candidate_id=cand.id, status="active", current_question_number=1, total_questions=5)
    db.add(session)
    db.commit()

    q1 = InterviewQuestion(session_id=session.id, question_number=1, question_text="Q1 text", topic="Database Performance", difficulty="Medium")
    db.add(q1)
    db.commit()
    s_id = session.id
    q1_id = q1.id
    db.close()

    # Submit Answer for Q1
    res = client.post(f"/api/interview/{s_id}/answer", json={"question_id": q1_id, "answer_text": "Detailed answer for Q1"})
    assert res.status_code == 200

    # Verify score & feedback persisted on InterviewAnswer
    db = SessionLocal()
    ans_db = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q1_id).first()
    assert ans_db is not None
    assert ans_db.score == 8.0
    assert ans_db.feedback == "Great technical answer."
    
    # Mark session completed to test report generation
    sess_db = db.query(InterviewSession).filter(InterviewSession.id == s_id).first()
    sess_db.status = "completed"
    db.commit()
    db.close()

    # Call GET /api/interview/{session_id}/report
    res_rep = client.get(f"/api/interview/{s_id}/report")
    assert res_rep.status_code == 200
    rep_data = res_rep.json()

    assert rep_data["session_id"] == s_id
    assert rep_data["overall_score"] > 0.0
    assert rep_data["recommendation"] in ["Strong Candidate", "Good Candidate", "Needs Improvement", "Significant Gaps"]
    assert "Candidate demonstrated strong" in rep_data["summary"]

    # Verify GET /api/interview/{session_id}/questions includes score and feedback
    res_qs = client.get(f"/api/interview/{s_id}/questions")
    assert res_qs.status_code == 200
    q_item = res_qs.json()["questions"][0]
    assert q_item["score"] == 8.0
    assert q_item["feedback"] == "Great technical answer."
    assert q_item["answer_text"] == "Detailed answer for Q1"
