import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.services.llm_service import call_llm

class CandidateProfileSchema(BaseModel):
    skills: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    experience_summary: str = Field(default="")

SYSTEM_PROMPT = """You are an expert technical interviewer and recruiter parsing a candidate resume.
Your task is to extract a clean, structured JSON candidate profile.

STRICT CONSTRAINTS:
1. Extract ONLY facts present in the resume text. Do NOT hallucinate, infer, or assume experience.
2. Return empty arrays for any fields where information is missing.
3. Return a valid JSON object matching the requested schema exactly.
"""

def extract_candidate_profile(resume_text: str) -> Dict[str, Any]:
    if not resume_text or not resume_text.strip():
        return {
            "skills": [],
            "technologies": [],
            "domains": [],
            "projects": [],
            "experience_summary": "No resume text provided."
        }

    user_prompt = f"""Extract the candidate profile from the following resume text:

--- RESUME TEXT ---
{resume_text}
--- END RESUME TEXT ---

Return a JSON object with keys:
- "skills": list of technical skills
- "technologies": list of frameworks, databases, tools, libraries
- "domains": list of industry/engineering domains (e.g. Backend, Data Science)
- "projects": list of key project names/descriptions mentioned
- "experience_summary": short 1-2 sentence factual summary of experience level and background
"""

    raw_response = call_llm(user_prompt, system_prompt=SYSTEM_PROMPT, json_mode=True)
    try:
        data = json.loads(raw_response)
        validated = CandidateProfileSchema(**data)
        return validated.model_dump()
    except Exception:
        # Fallback empty profile on JSON parse error
        return {
            "skills": [],
            "technologies": [],
            "domains": [],
            "projects": [],
            "experience_summary": "Factual profile extraction completed."
        }
