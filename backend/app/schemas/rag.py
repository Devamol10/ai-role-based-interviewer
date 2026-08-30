from typing import List
from pydantic import BaseModel, Field, field_validator
from app.rag.config import rag_config

class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    role: str = Field(..., description="Target role name")
    top_k: int = Field(5, ge=1, le=10, description="Number of top relevant chunks to retrieve")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query string cannot be empty.")
        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Role selection cannot be empty.")
        valid_roles = list(rag_config.ROLE_MAPPING.keys())
        if v not in valid_roles:
            raise ValueError(f"Unsupported role '{v}'. Must be one of: {', '.join(valid_roles)}")
        return v

class ChunkResult(BaseModel):
    text: str
    source: str
    role: str
    chunk_index: int

class RAGSearchResponse(BaseModel):
    query: str
    role: str
    result_count: int
    results: List[ChunkResult]
