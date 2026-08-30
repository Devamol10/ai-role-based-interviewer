# AI Role-Based Interviewer

**Repository:** https://github.com/Devamol10/ai-role-based-interviewer

AI Role-Based Interviewer is an intelligent technical interview platform designed to conduct role-based technical interviews for engineering candidates using candidate resumes and domain knowledge bases.

## Architecture Overview

The system follows a decoupled client-server architecture:
- **Frontend**: Single-page application built with React 19, Vite, TypeScript, and Tailwind CSS.
- **Backend**: RESTful API service built with FastAPI, Uvicorn, SQLAlchemy 2.x ORM, and Pydantic v2.
- **Database**: SQLite (`interviewer.db`) managed via SQLAlchemy ORM.
- **Vector Storage**: ChromaDB (`chromadb`) persistent vector collection (`./chroma_db`).
- **AI / LLM Engine**: OpenAI API (`text-embedding-3-small` embeddings and `gpt-4o-mini` chat completion model).

```text
Resume Upload + Role Selection
               │
               ▼
Candidate Persistence & Profile Extraction (skills, technologies)
               │
               ▼
Topic Selection & RAG Vector Retrieval (ChromaDB + OpenAI Embeddings)
               │
               ▼
Personalized AI Question Generation (Questions 1 - 5)
               │
               ▼
Candidate Answer Submission & AI Rubric Evaluation (0-10 Scale)
               │
               ▼
Final Executive Candidate Report (Python Averaged Score + Recommendation + Summary)
```

## Tech Stack

- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.0+, Pydantic v2
- **Vector DB & AI**: ChromaDB, OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`), PyMuPDF (`pymupdf`)
- **Testing**: pytest, httpx
- **Database**: SQLite (`interviewer.db`)
- **Containerization**: Docker & Docker Compose

## Quick Verification Commands for Reviewers

### 1. Run Complete Backend Test Suite
```bash
cd backend
# Activate virtual environment if not active:
# .\venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/Mac)
pytest ../tests
```

### 2. Verify Knowledge Base Vector Ingestion
```bash
cd backend
python scripts/ingest_knowledge_base.py
```

### 3. Run Frontend Production Build Check
```bash
cd frontend
npm run build
```

### 4. Start Local Development Servers

**Backend**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
*Health Check:* `http://localhost:8000/api/health`

**Frontend**:
```bash
cd frontend
npm run dev
```
*Application Access:* `http://localhost:5173`

## Database Entities

The SQLite database (`interviewer.db`) includes the following 5 ORM models:
1. **Candidate** (`candidates`): Stores candidate background info, resume text, target role, and extracted skills/technologies.
2. **InterviewSession** (`interview_sessions`): Tracks interview session status (`created`, `active`, `completed`), progress counters, and candidate relationship.
3. **InterviewQuestion** (`interview_questions`): Contains individual questions generated per session, question numbers, topics, difficulties, and RAG context.
4. **InterviewAnswer** (`interview_answers`): Holds candidate responses, evaluation scores (0-10 scale), and feedback per question.
5. **InterviewReport** (`interview_reports`): Stores overall candidate session scores, strengths, weaknesses, and performance summaries.

## Project Structure

```text
ai-role-based-interviewer/
│
├── frontend/             # React + Vite + TypeScript frontend application
│   ├── src/
│   │   ├── services/     # Centralized API service methods (api.ts)
│   │   ├── App.tsx       # Main React UI component
│   │   └── index.css     # Tailwind CSS setup
│   ├── .env.example
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # API route definitions and router
│   │   │   ├── routes/   # Route modules (health.py, resume.py, rag.py, questions.py, answers.py, reports.py)
│   │   │   └── router.py # Central API router aggregator
│   │   ├── core/         # Settings & SQLite DB engine configuration
│   │   ├── models/       # SQLAlchemy 2.x ORM database models
│   │   ├── schemas/      # Pydantic v2 request & response schemas
│   │   ├── services/     # Business logic & AI services (llm_service, resume_service, etc.)
│   │   ├── rag/          # RAG chunker, embeddings, vector_store, ingestion, retrieval
│   │   └── main.py       # FastAPI application entrypoint with lifespan DB init
│   ├── scripts/          # CLI ingestion scripts (ingest_knowledge_base.py)
│   └── requirements.txt
│
├── knowledge_base/       # Role-specific knowledge sources (.md/.txt)
│   ├── backend_engineer/
│   ├── ai_ml_engineer/
│   └── data_science/
│
├── tests/                # Pytest test suite & demo resume fixture
│   ├── test_backend.py
│   └── demo_resume.txt
│
├── .gitignore
├── .env.example
├── README.md
└── docker-compose.yml
```

## API Specification Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/resume/upload` | Upload PDF resume, extract text, and save candidate |
| `POST` | `/api/rag/search` | Search knowledge base chunks using role-filtered vector search |
| `POST` | `/api/interview/questions/generate` | Generate initial RAG-grounded personalized question |
| `POST` | `/api/interview/{session_id}/answer` | Submit candidate answer, evaluate score & feedback, advance session |
| `GET` | `/api/interview/{session_id}` | Retrieve current session state and active question |
| `GET` | `/api/interview/{session_id}/questions` | List all session questions with evaluation scores and feedback |
| `GET` | `/api/interview/{session_id}/report` | Retrieve or generate final candidate assessment report |

## Evaluation Rubric & Recommendation Logic

### Evaluation Rubric (0–10 Scale)
- **0–2**: Incorrect or largely irrelevant.
- **3–4**: Limited understanding with significant technical gaps.
- **5–6**: Basic understanding with meaningful gaps or missing details.
- **7–8**: Good understanding with minor gaps or slight trade-off oversights.
- **9–10**: Strong, comprehensive, and technically accurate answer.

### Deterministic Recommendation Logic
- **8.5 – 10.0**: `Strong Candidate`
- **7.0 – 8.49**: `Good Candidate`
- **5.0 – 6.99**: `Needs Improvement`
- **0.0 – 4.99**: `Significant Gaps`
