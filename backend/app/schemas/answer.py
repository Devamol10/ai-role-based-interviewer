from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class InterviewAnswerCreate(BaseModel):
    question_id: int
    answer_text: str

    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid question ID")
        return v

    @field_validator("answer_text")
    @classmethod
    def validate_answer(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Answer text cannot be empty")
        return v.strip()

class InterviewAnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
