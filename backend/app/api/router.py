from fastapi import APIRouter
from app.api.routes.health import router as health_router

api_router = APIRouter()

# Main health endpoint
api_router.include_router(health_router)

# Placeholder route registration for future modules:
# api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
# api_router.include_router(interview_router, prefix="/interview", tags=["Interview"])
# api_router.include_router(questions_router, prefix="/questions", tags=["Questions"])
# api_router.include_router(results_router, prefix="/results", tags=["Results"])
