from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate import Candidate
from app.services.resume_service import extract_text_from_pdf
from app.schemas.resume import ResumeUploadResponse

router = APIRouter()

ALLOWED_ROLES = [
    "Backend Engineer",
    "AI/ML Engineer",
    "Data Science / Applied ML"
]

@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    cleaned_role = role.strip() if role else ""
    if not cleaned_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role selection is required and cannot be empty."
        )

    if cleaned_role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(ALLOWED_ROLES)}"
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a .pdf file."
        )

    file_bytes = await file.read()
    
    # Extract text page by page
    extracted_text = extract_text_from_pdf(file_bytes, file.filename)

    # Save candidate in database
    candidate = Candidate(
        resume_filename=file.filename,
        resume_text=extracted_text,
        selected_role=cleaned_role,
        extracted_skills=[],
        extracted_technologies=[]
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        filename=candidate.resume_filename,
        selected_role=candidate.selected_role,
        extracted_text_length=len(extracted_text),
        message="Resume uploaded and text extracted successfully."
    )
