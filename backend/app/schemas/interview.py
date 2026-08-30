from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class InterviewSessionCreate(BaseModel):
    candidate_id: int
    total_questions: Optional[int] = 5

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid candidate ID")
        return v

class InterviewSessionResponse(BaseModel):
    id: int
    candidate_id: int
    status: str
    current_question_number: int
    total_questions: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
