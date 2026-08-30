# AI Role-Based Interviewer

AI Role-Based Interviewer is an intelligent technical interview platform designed to conduct role-based technical interviews for engineering candidates using candidate resumes and domain knowledge bases.

## Current Architecture Overview

The system follows a decoupled client-server architecture:
- **Frontend**: Single-page application built with React, Vite, TypeScript, and Tailwind CSS.
- **Backend**: RESTful API service built with FastAPI, Uvicorn, and Pydantic.
- **Database**: SQLite (configured for initial local persistence).
- **Knowledge Base & RAG**: Dedicated folder directory and module layout structured for vector embeddings and document processing.

## Tech Stack

- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2
- **Database**: SQLite (SQLAlchemy / direct DB connection ready)
- **Containerization**: Docker & Docker Compose

## Project Structure

```text
ai-role-based-interviewer/
│
├── frontend/             # React + Vite + TypeScript frontend application
│
├── backend/              # FastAPI application
│   └── app/
│       ├── api/          # API route endpoints
│       ├── core/         # Settings & app configurations
│       ├── models/       # Database models
│       ├── schemas/      # Pydantic schemas
│       ├── services/     # Core business logic
│       ├── rag/          # Vector search & RAG pipeline
│       ├── utils/        # Helper functions
│       └── main.py       # FastAPI application entrypoint
│
├── knowledge_base/       # Storage for role knowledge documents
├── tests/                # Test suite
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

### 3. Frontend Setup & Run Command

Navigate to the `frontend/` folder:
```bash
cd frontend
npm install
npm run dev
```
The frontend application will be accessible at: `http://localhost:5173`

## Current Project Status

- [x] Base project repository structure initialized.
- [x] FastAPI modular app setup with CORS middleware.
- [x] `GET /api/health` endpoint implemented and verified.
- [x] React + Vite + TypeScript frontend landing page created with backend health connection indicator.
- [x] Configuration files (`.env.example`, `.gitignore`, `docker-compose.yml`) established.

## Planned Upcoming Modules

1. **Resume Ingestion & Parsing**: Extract text & structure from candidate PDF resumes (PyMuPDF).
2. **Knowledge Base RAG Engine**: Index documents into ChromaDB vector store and retrieve relevant domain context based on target roles.
3. **Interactive LLM Interview Pipeline**: Question generation & context-aware follow-ups powered by OpenAI API.
4. **Candidate Response Evaluation & Report Generation**: Score candidate technical answers and generate summary feedback reports.
