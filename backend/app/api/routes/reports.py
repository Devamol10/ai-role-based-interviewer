import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion
from app.models.answer import InterviewAnswer
from app.models.report import InterviewReport
from app.schemas.report_response import InterviewReportResponse
from app.services.report_service import get_recommendation_label, generate_summary

router = APIRouter()

@router.get("/{session_id}/report", response_model=InterviewReportResponse)
def get_or_generate_interview_report(
    session_id: int,
    db: Session = Depends(get_db)
):
    # 1. Validate session
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found."
        )

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview session {session_id} is not completed yet."
        )

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()
    role_name = candidate.selected_role if candidate else "Software Engineer"

    # 2. Check if report already exists in SQLite
    existing_report = db.query(InterviewReport).filter(InterviewReport.session_id == session.id).first()
    if existing_report:
        rec_label = get_recommendation_label(existing_report.overall_score)
        return InterviewReportResponse(
            session_id=session.id,
            overall_score=existing_report.overall_score,
            recommendation=rec_label,
            strengths=existing_report.strengths or [],
            weaknesses=existing_report.weaknesses or [],
            summary=existing_report.summary,
            question_count=session.total_questions
        )

    # 3. Gather questions and evaluated answers
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(InterviewQuestion.question_number.asc()).all()

    scores = []
    strengths_set = set()
    weaknesses_set = set()
    qa_evals = []

    for q in questions:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        score = ans.score if (ans and ans.score is not None) else 5.0
        scores.append(score)

        if score >= 7.0:
            strengths_set.add(f"Strong understanding of {q.topic or 'technical concepts'}")
        elif score < 6.0:
            weaknesses_set.add(f"Gaps identified in {q.topic or 'applied engineering'}")

        qa_evals.append({
            "topic": q.topic,
            "score": score,
            "feedback": ans.feedback if ans else ""
        })

    # Calculate numeric average in Python
    overall_score = round(sum(scores) / len(scores), 1) if scores else 0.0
    recommendation = get_recommendation_label(overall_score)

    strengths_list = list(strengths_set) if strengths_set else ["Demonstrated core technical participation."]
    weaknesses_list = list(weaknesses_set) if weaknesses_set else ["No critical technical gaps identified."]

    # Generate qualitative summary using LLM
    summary_text = generate_summary(
        role=role_name,
        overall_score=overall_score,
        qa_evaluations=qa_evals,
        strengths=strengths_list,
        weaknesses=weaknesses_list
    )

    # Persist report in SQLite
    new_report = InterviewReport(
        session_id=session.id,
        overall_score=overall_score,
        strengths=strengths_list,
        weaknesses=weaknesses_list,
        summary=summary_text
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return InterviewReportResponse(
        session_id=session.id,
        overall_score=new_report.overall_score,
        recommendation=recommendation,
        strengths=new_report.strengths or [],
        weaknesses=new_report.weaknesses or [],
        summary=new_report.summary,
        question_count=session.total_questions
    )
