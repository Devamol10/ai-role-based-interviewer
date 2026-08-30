from pydantic import BaseModel

class ResumeUploadResponse(BaseModel):
    candidate_id: int
    filename: str
    selected_role: str
    extracted_text_length: int
    message: str
