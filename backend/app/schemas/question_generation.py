import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator

class QuestionGenerateRequest(BaseModel):
    candidate_id: int = Field(..., description="ID of the candidate")
    topic: Optional[str] = Field(None, description="Optional target interview topic")

    @field_validator("candidate_id")
    @classmethod
    def validate_candidate_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Invalid candidate_id")
        return v

class RetrievedContextItem(BaseModel):
    text: str
    source: str
    role: str
    chunk_index: int

class QuestionGenerateResponse(BaseModel):
    id: int
    session_id: int
    question_number: int
    question_text: str
    topic: str
    difficulty: str
    reason: str
    retrieved_context: List[RetrievedContextItem]
