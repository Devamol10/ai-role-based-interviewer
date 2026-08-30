# AI Role-Based Interviewer — Demo Video Script

**Target Duration:** 3–5 Minutes  
**Audience:** Technical Reviewers & Hiring Managers  

---

### 0:00 – 0:20 | Introduction
**Visual:** Show the application landing page (`http://localhost:5173`) with the title "AI Role-Based Interviewer".  
**Speaker Script:**  
"Hello! Today I'm demonstrating the AI Role-Based Interviewer — an intelligent technical interview platform I built. The system parses a candidate's resume, accepts a target engineering role, and retrieves role-specific knowledge from a RAG vector database to generate adaptive 5-question technical interviews, grade candidate answers against a rubric, and produce an executive evaluation report."

---

### 0:20 – 0:45 | Architecture Overview
**Visual:** Briefly show the Mermaid architecture diagram or directory structure.  
**Speaker Script:**  
"Architecturally, the application uses a React and TypeScript frontend communicating with a FastAPI backend. For data persistence, SQLite stores session records while ChromaDB holds embedded domain knowledge chunks. OpenAI's `gpt-4o-mini` model powers resume profiling, question generation, and answer evaluations, while `text-embedding-3-small` generates semantic vector embeddings."

---

### 0:45 – 1:10 | Resume Upload & Candidate Setup
**Visual:** Drag and drop `docs/demo-resume.md` (or converted PDF), select **Backend Engineer** from the dropdown, and click **Upload Resume & Start Interview**.  
**Speaker Script:**  
"Let's start by uploading our synthetic candidate resume for a Backend Engineer position. Once submitted, FastAPI extracts the text using PyMuPDF, extracts key skills like Python, FastAPI, PostgreSQL, and Redis, and creates an active interview session in SQLite."

---

### 1:10 – 2:30 | Interactive RAG-Grounded Interview (Questions 1 to 5)
**Visual:** Display Question 1 on screen. Point out the topic banner ("Topic: Database Performance") and difficulty tag.  
**Speaker Script:**  
"Here is Question 1. Notice how the system retrieved grounded domain knowledge from ChromaDB regarding database indexing and combined it with the candidate's background in PostgreSQL. Let's type a technical response explaining B-Tree indexes and query execution plans."

*(Actions: Submit answer for Q1 → show loading state → advance through Questions 2 to 5 with brief answers).*  

"As we progress through the 5 questions, the backend tracks unvisited topics and uses past question-and-answer pairs to probe deeper applied engineering concepts without repeating subjects."

---

### 2:30 – 3:20 | Answer Evaluation & Rubric
**Visual:** Submit Question 5. Show the transition loading indicator ("Evaluating Final Answer & Generating Report...").  
**Speaker Script:**  
"Upon submitting each answer, FastAPI sends the response, the question, and the exact retrieved RAG context to OpenAI for grading against a standardized 0-to-10 evaluation rubric. Scores and feedback are saved directly to SQLite."

---

### 3:20 – 4:00 | Final Candidate Report & Wrap-Up
**Visual:** Scroll through the generated Final Report dashboard showing:
- Overall Score (e.g., `7.8 / 10`)
- Recommendation Badge (`Good Candidate`)
- Key Strengths & Areas to Improve
- Executive Summary
- Expandable Per-Question Breakdown  

**Speaker Script:**  
"Once Question 5 is completed, the system calculates the overall score deterministically in Python as the numerical average, maps it to a hiring recommendation like 'Good Candidate', and generates an executive summary. Reviewers can also expand each question to review submitted text alongside AI-generated feedback.

To recap, the key technical highlights are FastAPI orchestration, ChromaDB vector retrieval with strict grounding checks, SQLite persistence, and a responsive React UI. Thank you for watching!"
