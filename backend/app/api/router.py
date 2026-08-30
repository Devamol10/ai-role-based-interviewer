from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.resume import router as resume_router
from app.api.routes.rag import router as rag_router
from app.api.routes.questions import router as questions_router
from app.api.routes.answers import router as answers_router
from app.api.routes.reports import router as reports_router

api_router = APIRouter()

# Register API routers
api_router.include_router(health_router)
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
api_router.include_router(questions_router, prefix="/interview/questions", tags=["Questions"])
api_router.include_router(answers_router, prefix="/interview", tags=["Interview"])
api_router.include_router(reports_router, prefix="/interview", tags=["Reports"])
