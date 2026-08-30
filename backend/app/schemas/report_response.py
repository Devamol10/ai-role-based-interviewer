from pydantic import BaseModel
from typing import List, Optional

class InterviewReportResponse(BaseModel):
    session_id: int
    overall_score: float
    recommendation: str
    strengths: List[str] = []
    weaknesses: List[str] = []
    summary: str
    question_count: int
