from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator

class InterviewQuestionResponse(BaseModel):
    id: int
    session_id: int
    question_number: int
    question_text: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
