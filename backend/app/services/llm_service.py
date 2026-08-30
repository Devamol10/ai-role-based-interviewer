from typing import Any, Optional
import json
from openai import OpenAI
from fastapi import HTTPException, status

from app.core.config import settings

def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_mode: bool = True
) -> str:
    """
    Centralized OpenAI Chat Completion caller with dynamic mock fallback for API key omission.
    """
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        # Dynamic Mock mode fallback for seamless local demo without requiring a paid API key
        if "Extract the candidate profile" in prompt or "CandidateProfileSchema" in prompt:
            return json.dumps({
                "skills": ["Python", "FastAPI", "REST APIs", "SQL", "Docker"],
                "technologies": ["FastAPI", "PostgreSQL", "SQLite", "Redis", "Docker", "PyTest"],
                "domains": ["Backend Engineering", "API Design", "Distributed Systems"],
                "projects": ["High-throughput Microservices", "Cache-Aside Optimization"],
                "experience_summary": "Experienced Backend Software Engineer with expertise in building scalable REST APIs and database tuning."
            })
        elif "Evaluate the candidate's answer" in prompt or "EVALUATION RUBRIC" in (system_prompt or ""):
            return json.dumps({
                "score": 8.5,
                "feedback": "Strong and technically accurate explanation demonstrating good practical understanding of trade-offs.",
                "strengths": [
                    "Correctly articulated core technical concepts",
                    "Demonstrated real-world system design awareness"
                ],
                "improvements": [
                    "Could expand on edge-case failure handling and monitor metrics"
                ]
            })
        elif "Write a professional, concise executive summary" in prompt or "executive candidate assessment" in (system_prompt or ""):
            return json.dumps({
                "summary": "The candidate performed exceptionally well across all technical domains, demonstrating strong backend software engineering concepts, solid database optimization skills, and clear communication of system trade-offs."
            })
        else:
            # Default mock question generation response
            return json.dumps({
                "question": "How would you design a caching layer using Redis to optimize high-traffic database queries while avoiding cache stampede?",
                "topic": "System Design & Caching",
                "difficulty": "Medium",
                "reason": "Selected based on backend role alignment and database/caching background."
            })

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response_format = {"type": "json_object"} if json_mode else None

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            response_format=response_format,
            temperature=0.7
        )

        return response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OpenAI service call failed: {str(e)}"
        )
