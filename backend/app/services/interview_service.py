import json
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.interview import InterviewSession
from app.models.question import InterviewQuestion
from app.models.answer import InterviewAnswer
from app.services.topic_service import select_interview_topics
from app.services.question_generation_service import generate_interview_question
from app.services.answer_evaluation_service import evaluate_answer

TOTAL_INTERVIEW_QUESTIONS = 5

def process_candidate_answer(
    session_id: int,
    question_id: int,
    answer_text: str,
    db: Session
) -> Dict[str, Any]:
    # 1. Validate Session
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found."
        )

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interview session {session_id} is not active."
        )

    # 2. Validate Question
    question = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview question {question_id} not found."
        )

    if question.session_id != session.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question {question_id} does not belong to session {session_id}."
        )

    # Check for duplicate answer
    existing_answer = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == question.id).first()
    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An answer for question {question.question_number} has already been submitted."
        )

    candidate = db.query(Candidate).filter(Candidate.id == session.candidate_id).first()

    # 3. Retrieve RAG grounding context stored with question
    retrieved_ctx = []
    if question.retrieved_context:
        try:
            retrieved_ctx = json.loads(question.retrieved_context)
        except Exception:
            retrieved_ctx = []

    # 4. Perform AI Answer Evaluation
    eval_result = evaluate_answer(
        question_text=question.question_text,
        answer_text=answer_text,
        role=candidate.selected_role,
        topic=question.topic or "Technical",
        retrieved_context=retrieved_ctx
    )

    # 5. Persist InterviewAnswer with score and feedback in SQLite
    new_answer = InterviewAnswer(
        question_id=question.id,
        answer_text=answer_text.strip(),
        score=eval_result.get("score"),
        feedback=eval_result.get("feedback")
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    current_q_num = session.current_question_number

    # 6. Check if interview is completed (Question 5 answered)
    if current_q_num >= TOTAL_INTERVIEW_QUESTIONS:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)

        return {
            "message": "Answer evaluated and recorded. Interview completed!",
            "session_id": session.id,
            "question_id": question.id,
            "next_question_number": None,
            "interview_completed": True,
            "next_question": None
        }

    # 7. Advance to next question (Question 2 to 5)
    next_q_num = current_q_num + 1
    session.current_question_number = next_q_num

    candidate_profile = {
        "skills": candidate.extracted_skills or [],
        "technologies": candidate.extracted_technologies or [],
        "experience_summary": f"Target role: {candidate.selected_role}"
    }

    # Gather past questions and answers for context
    past_questions_db = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session.id
    ).order_by(InterviewQuestion.question_number.asc()).all()

    past_context = []
    covered_topics = set()
    for pq in past_questions_db:
        if pq.topic:
            covered_topics.add(pq.topic)
        pa = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == pq.id).first()
        past_context.append({
            "question": pq.question_text,
            "topic": pq.topic or "",
            "answer": pa.answer_text if pa else ""
        })

    # Select next unvisited topic
    all_topics = select_interview_topics(candidate_profile, candidate.selected_role)
    next_topic = None
    for t in all_topics:
        if t not in covered_topics:
            next_topic = t
            break
    if not next_topic:
        next_topic = all_topics[(next_q_num - 1) % len(all_topics)] if all_topics else "Advanced Engineering"

    # Generate next question with previous context
    question_data = generate_interview_question(
        candidate_profile=candidate_profile,
        role=candidate.selected_role,
        topic=next_topic,
        past_questions_context=past_context
    )

    next_db_question = InterviewQuestion(
        session_id=session.id,
        question_number=next_q_num,
        question_text=question_data["question"],
        topic=question_data["topic"],
        difficulty=question_data["difficulty"],
        retrieved_context=json.dumps(question_data["retrieved_context"])
    )
    db.add(next_db_question)
    db.commit()
    db.refresh(next_db_question)

    return {
        "message": "Answer evaluated and recorded successfully.",
        "session_id": session.id,
        "question_id": question.id,
        "next_question_number": next_q_num,
        "interview_completed": False,
        "next_question": {
            "id": next_db_question.id,
            "session_id": session.id,
            "question_number": next_db_question.question_number,
            "question_text": next_db_question.question_text,
            "topic": next_db_question.topic,
            "difficulty": next_db_question.difficulty,
            "reason": question_data.get("reason", ""),
            "retrieved_context": question_data["retrieved_context"]
        }
    }
