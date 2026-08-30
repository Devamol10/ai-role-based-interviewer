from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class InterviewReportResponse(BaseModel):
    id: int
    session_id: int
    overall_score: float
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    summary: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
