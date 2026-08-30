import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion
from app.models.answer import InterviewAnswer
from app.schemas.answer_submit import AnswerSubmitRequest, AnswerSubmitResponse
from app.services.interview_service import process_candidate_answer

router = APIRouter()

@router.post("/{session_id}/answer", response_model=AnswerSubmitResponse)
def submit_answer(
    session_id: int,
    request: AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    return process_candidate_answer(
        session_id=session_id,
        question_id=request.question_id,
        answer_text=request.answer_text,
        db=db
    )

@router.get("/{session_id}")
def get_interview_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found."
        )

    current_question = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id,
        InterviewQuestion.question_number == session.current_question_number
    ).first()

    has_answer = False
    if current_question:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == current_question.id).first()
        has_answer = ans is not None

    return {
        "session_id": session.id,
        "candidate_id": session.candidate_id,
        "status": session.status,
        "current_question_number": session.current_question_number,
        "total_questions": session.total_questions,
        "current_question": {
            "id": current_question.id,
            "question_number": current_question.question_number,
            "question_text": current_question.question_text,
            "topic": current_question.topic,
            "difficulty": current_question.difficulty,
            "retrieved_context": json.loads(current_question.retrieved_context) if current_question.retrieved_context else []
        } if current_question else None,
        "answer_submitted": has_answer
    }

@router.get("/{session_id}/questions")
def get_interview_questions(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found."
        )

    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(InterviewQuestion.question_number.asc()).all()

    result = []
    for q in questions:
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == q.id).first()
        result.append({
            "id": q.id,
            "question_number": q.question_number,
            "question_text": q.question_text,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "answer_submitted": ans is not None
        })

    return {
        "session_id": session.id,
        "total_questions": len(result),
        "questions": result
    }
