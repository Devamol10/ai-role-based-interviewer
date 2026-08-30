from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_text: Mapped[str] = mapped_column(String, nullable=False)
    selected_role: Mapped[str] = mapped_column(String(100), nullable=False)
    extracted_skills: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    extracted_technologies: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    sessions: Mapped[List["InterviewSession"]] = relationship("InterviewSession", back_populates="candidate", cascade="all, delete-orphan")
