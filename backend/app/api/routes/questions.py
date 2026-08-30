import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion
from app.schemas.question_generation import QuestionGenerateRequest, QuestionGenerateResponse
from app.services.candidate_profile_service import extract_candidate_profile
from app.services.topic_service import select_interview_topics
from app.services.question_generation_service import generate_interview_question

router = APIRouter()

@router.post("/generate", response_model=QuestionGenerateResponse, status_code=status.HTTP_201_CREATED)
def generate_question_for_candidate(
    request: QuestionGenerateRequest,
    db: Session = Depends(get_db)
):
    # 1. Load and validate candidate
    candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with ID {request.candidate_id} not found."
        )

    if not candidate.selected_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate does not have a selected role."
        )

    if not candidate.resume_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate does not have resume text."
        )

    # 2. Extract / Update candidate profile if not already populated
    if not candidate.extracted_skills or not candidate.extracted_technologies:
        profile = extract_candidate_profile(candidate.resume_text)
        candidate.extracted_skills = profile.get("skills", [])
        candidate.extracted_technologies = profile.get("technologies", [])
        db.commit()
        db.refresh(candidate)

    candidate_profile = {
        "skills": candidate.extracted_skills or [],
        "technologies": candidate.extracted_technologies or [],
        "experience_summary": f"Target role: {candidate.selected_role}"
    }

    # 3. Topic selection
    topic = request.topic
    if not topic or not topic.strip():
        selected_topics = select_interview_topics(candidate_profile, candidate.selected_role)
        topic = selected_topics[0] if selected_topics else "Core Engineering Concepts"

    # 4. Find or create InterviewSession
    session = db.query(InterviewSession).filter(
        InterviewSession.candidate_id == candidate.id,
        InterviewSession.status == "active"
    ).first()

    if not session:
        session = InterviewSession(
            candidate_id=candidate.id,
            status="active",
            current_question_number=1,
            total_questions=5
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 5. Generate RAG-grounded interview question
    question_data = generate_interview_question(
        candidate_profile=candidate_profile,
        role=candidate.selected_role,
        topic=topic
    )

    # 6. Save InterviewQuestion to SQLite
    db_question = InterviewQuestion(
        session_id=session.id,
        question_number=session.current_question_number,
        question_text=question_data["question"],
        topic=question_data["topic"],
        difficulty=question_data["difficulty"],
        retrieved_context=json.dumps(question_data["retrieved_context"])
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return QuestionGenerateResponse(
        id=db_question.id,
        session_id=session.id,
        question_number=db_question.question_number,
        question_text=db_question.question_text,
        topic=db_question.topic or topic,
        difficulty=db_question.difficulty or "Medium",
        reason=question_data.get("reason", ""),
        retrieved_context=question_data["retrieved_context"]
    )
