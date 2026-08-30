from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.resume import router as resume_router

api_router = APIRouter()

# Register routes
api_router.include_router(health_router)
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
