import sys
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy import inspect

# Add backend directory to path so app imports resolve
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.database import engine, init_db

client = TestClient(app)

def test_health_endpoint_status():
    response = client.get("/api/health")
    assert response.status_code == 200

def test_health_endpoint_response_body():
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-role-based-interviewer"

def test_database_initialization():
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = {
        "candidates",
        "interview_sessions",
        "interview_questions",
        "interview_answers",
        "interview_reports",
    }
    for table in expected_tables:
        assert table in tables
