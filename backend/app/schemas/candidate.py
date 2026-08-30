from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class CandidateBase(BaseModel):
    selected_role: str

    @field_validator("selected_role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Role cannot be empty")
        return v.strip()

class CandidateCreate(CandidateBase):
    resume_filename: str
    resume_text: str
    extracted_skills: Optional[List[str]] = []
    extracted_technologies: Optional[List[str]] = []

class CandidateResponse(CandidateBase):
    id: int
    resume_filename: str
    extracted_skills: Optional[List[str]] = []
    extracted_technologies: Optional[List[str]] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
