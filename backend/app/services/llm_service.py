from typing import Any, Optional
from openai import OpenAI
from fastapi import HTTPException, status

from app.core.config import settings

def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_mode: bool = True
) -> str:
    """
    Centralized OpenAI Chat Completion caller.
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is missing. Set OPENAI_API_KEY environment variable to enable AI capabilities."
        )

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
