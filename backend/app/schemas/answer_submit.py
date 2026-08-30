from pydantic import BaseModel, Field, field_validator

class AnswerSubmitRequest(BaseModel):
    question_id: int = Field(..., description="ID of the question being answered")
    answer_text: str = Field(..., description="Candidate's answer text")

    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid question_id")
        return v

    @field_validator("answer_text")
    @classmethod
    def validate_answer_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Answer text cannot be empty.")
        if len(v.strip()) < 5:
            raise ValueError("Answer text is too short. Please provide a substantive response.")
        return v.strip()

class AnswerSubmitResponse(BaseModel):
    message: str
    session_id: int
    question_id: int
    next_question_number: int | None = None
    interview_completed: bool
    next_question: dict | None = None
