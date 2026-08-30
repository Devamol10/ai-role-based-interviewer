from datetime import datetime
from typing import Optional
from sqlalchemy import Float, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("interview_sessions.id"), nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    strengths: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    weaknesses: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["InterviewSession"] = relationship("InterviewSession", back_populates="report")
