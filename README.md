# AI Role-Based Interviewer

**Repository:** https://github.com/Devamol10/ai-role-based-interviewer

AI Role-Based Interviewer is an intelligent technical interview platform designed to conduct role-based technical interviews for engineering candidates using candidate resumes and domain knowledge bases.

## Architecture Overview

The system follows a decoupled client-server architecture:
- **Frontend**: Single-page application built with React 19, Vite, TypeScript, and Tailwind CSS.
- **Backend**: RESTful API service built with FastAPI, Uvicorn, SQLAlchemy 2.x ORM, and Pydantic v2.
- **Database**: SQLite (managed with SQLAlchemy ORM).
- **Knowledge Base & RAG**: Dedicated folder directory and module layout structured for vector embeddings and document processing.

## Tech Stack

- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy 2.0+, Pydantic v2
- **Testing**: pytest, httpx
- **Database**: SQLite (`interviewer.db`)
- **Containerization**: Docker & Docker Compose

## Database Entities

The SQLite database (`interviewer.db`) includes the following 5 ORM models:
1. **Candidate** (`candidates`): Stores candidate background info, resume text, target role, and extracted skills/technologies.
2. **InterviewSession** (`interview_sessions`): Tracks interview session status (`created`, `in_progress`, `completed`), progress counters, and candidate relationship.
3. **InterviewQuestion** (`interview_questions`): Contains individual questions generated per session, question numbers, topics, difficulties, and RAG context.
4. **InterviewAnswer** (`interview_answers`): Holds candidate responses, evaluation scores, and feedback per question.
5. **InterviewReport** (`interview_reports`): Stores overall candidate session scores, strengths, weaknesses, and performance summaries.

## Project Structure

```text
ai-role-based-interviewer/
│
├── frontend/             # React + Vite + TypeScript frontend application
│
├── backend/              # FastAPI application
│   └── app/
│       ├── api/          # API route definitions and router
│       │   ├── routes/   # Modular route handlers (e.g. health.py)
│       │   └── router.py # Central API router aggregator
│       ├── core/         # Settings & SQLite DB engine configuration
│       ├── models/       # SQLAlchemy 2.x ORM database models
│       ├── schemas/      # Pydantic v2 request & response schemas
│       ├── services/     # Core business logic (reserved)
│       ├── rag/          # Vector search & RAG pipeline (reserved)
│       ├── utils/        # Helper functions (reserved)
│       └── main.py       # FastAPI application entrypoint with lifespan DB init
│
├── knowledge_base/       # Storage for role knowledge documents
├── tests/                # Pytest test suite (backend & DB tests)
│
├── .gitignore
├── .env.example
├── README.md
└── docker-compose.yml
```

## Local Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)

### 1. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Backend Setup & Run Command

Navigate to the `backend/` folder:
```bash
cd backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
The backend health check will be accessible at: `http://localhost:8000/api/health`

### 3. Running Backend Tests

Navigate to the `backend/` folder with virtual environment active:
```bash
pytest ../tests
```

### 4. Frontend Setup & Run Command

Navigate to the `frontend/` folder:
```bash
cd frontend
npm install
npm run dev
```
The frontend application will be accessible at: `http://localhost:5173`

## Current Project Status

- [x] Base project repository structure initialized.
- [x] FastAPI modular app setup with CORS middleware and global exception handling.
- [x] SQLite database connection & SQLAlchemy 2.x models setup.
- [x] Resume PDF upload & PyMuPDF text extraction service implemented.
- [x] `POST /api/resume/upload` endpoint implemented with PDF/role validation and Candidate DB persistence.
- [x] React + Vite + TypeScript frontend upload interface with role selection and upload feedback.
- [x] Automated backend tests (`pytest`) covering health check, DB initialization, and resume upload edge cases.

## Resume Upload Feature

### Supported Roles
- `Backend Engineer`
- `AI/ML Engineer`
- `Data Science / Applied ML`

### PDF Extraction Technology
Uses **PyMuPDF** (`pymupdf`) to extract clean page-by-page text from uploaded PDF resumes without external binary dependencies.

### API Endpoint: `POST /api/resume/upload`
- **Request**: `multipart/form-data` containing `file` (PDF, max 5 MB) and `role`.
- **Response**:
  ```json
  {
    "candidate_id": 1,
    "filename": "resume.pdf",
    "selected_role": "Backend Engineer",
    "extracted_text_length": 1420,
    "message": "Resume uploaded and text extracted successfully."
  }
  ```

## RAG Architecture

The Knowledge Base Retrieval-Augmented Generation (RAG) module enables context-aware search over domain technical documentation:

```text
Resume + Role Selection
         │
         ▼
Target Role Mapping (e.g. Backend Engineer -> backend_engineer)
         │
         ▼
Query / Topic Construction ──► Embeddings (text-embedding-3-small)
                                      │
                                      ▼
Knowledge Base (.md/.txt) ──► ChromaDB Vector Store (Cosine Similarity)
                                      │
                                      ▼
                        Top-K Context Chunks Returned
```

### Why ChromaDB & Embeddings?
- **ChromaDB**: High-performance persistent vector database that stores chunk text, dense float vector embeddings, and chunk metadata locally (`./chroma_db`).
- **OpenAI Embeddings**: Converts query text and document chunks into dense 1536-dimensional vector representations using `text-embedding-3-small`.

### Chunking Strategy & Role Filtering
- **Paragraph-Aware Chunking**: Chunks document text into ~900 character windows with a 150-character overlap while preserving paragraph boundaries (`app/rag/chunker.py`).
- **Metadata**: Each chunk stores `source` filename, `role` tag, and deterministic `chunk_index`.
- **Role Filtering**: Vector queries filter ChromaDB collections by the candidate's target role (`backend_engineer`, `ai_ml_engineer`, `data_science`) to prevent cross-domain noise.

### Ingestion Script
To populate ChromaDB with the reference technical documents:
```bash
cd backend
python scripts/ingest_knowledge_base.py
```

### RAG Search API: `POST /api/rag/search`
- **Request Body**:
  ```json
  {
    "query": "How do B-Trees optimize indexing performance?",
    "role": "Backend Engineer",
    "top_k": 5
  }
  ```
- **Response**:
  ```json
  {
    "query": "How do B-Trees optimize indexing performance?",
    "role": "Backend Engineer",
    "result_count": 1,
    "results": [
      {
        "text": "Database indexing utilizes B-Trees and Hash Indexes to accelerate lookup queries...",
        "source": "databases.md",
        "role": "backend_engineer",
        "chunk_index": 0
      }
    ]
  }
  ```

## AI Question Generation Pipeline

The system converts raw candidate resumes and target roles into personalized, knowledge-grounded technical interview questions:

```text
Resume Text
     │
     ▼
Candidate Profile Extraction (app/services/candidate_profile_service.py)
     │
     ▼
Topic Selection (app/services/topic_service.py)
     │
     ▼
RAG Vector Retrieval (app/rag/retrieval.py)
     │
     ▼
LLM Question Generation (app/services/question_generation_service.py)
     │
     ▼
SQLite Persistence (InterviewSession & InterviewQuestion)
```

### Key Components:
- **Profile Extraction**: Extracts factual skills and technologies from resumes without hallucinating non-existent candidate experience.
- **Topic Selection**: Selects 3-5 relevant interview topics grounded in candidate skills and role demands.
- **RAG Grounding**: Combines role, candidate skills, and topic into vector queries to retrieve up to 3 domain-specific chunks from ChromaDB.
- **Question Generation**: OpenAI `gpt-4o-mini` crafts structured single questions tailored to candidate background and grounded in retrieved context.

## Interactive 5-Question Interview Flow

```text
Resume Upload + Role Selection
               │
               ▼
Candidate Created & Profile Extracted
               │
               ▼
Question 1 Generated (Topic A + RAG Context)
               │
               ▼
Candidate Answer Submitted (POST /api/interview/{session_id}/answer)
               │
               ▼
Next Question Generated (Questions 2 to 5 with Past Q&A Context + Unvisited Topics)
               │
               ▼
Question 5 Answered ──► Session Marked Completed (completed_at set) ──► Completion Screen
```

### Endpoints
1. `POST /api/interview/{session_id}/answer`: Validates answer length, prevents duplicate submissions per question, persists `InterviewAnswer` in SQLite, advances `current_question_number`, retrieves RAG context, and returns the next question. Upon answering Question 5, sets `interview_completed: true` and marks session `completed`.
2. `GET /api/interview/{session_id}`: Returns current session status, question number, active question text, and submission status for session recovery.
3. `GET /api/interview/{session_id}/questions`: Returns structured history of all generated questions in sequence.

## Planned Upcoming Modules

1. **Resume Ingestion & Parsing**: Extract text & structure from candidate PDF resumes (PyMuPDF).
2. **Knowledge Base RAG Engine**: Index documents into ChromaDB vector store and retrieve relevant domain context based on target roles.
3. **Interactive LLM Interview Pipeline**: Question generation & context-aware follow-ups powered by OpenAI API.
4. **Candidate Response Evaluation & Report Generation**: Score candidate technical answers and generate summary feedback reports.
