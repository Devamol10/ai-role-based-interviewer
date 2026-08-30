# AI Role-Based Interviewer — Demo Recording Checklist

Use this checklist to ensure a clean, professional, and secure recording session.

---

## 1. Pre-Recording Setup Checklist
- [ ] **API Key Configured**: `OPENAI_API_KEY` set in `backend/.env`.
- [ ] **Knowledge Base Ingested**: Executed `python scripts/ingest_knowledge_base.py` in `backend/`.
- [ ] **ChromaDB Initialized**: Verified persistent collection at `backend/chroma_db/`.
- [ ] **Backend Running**: Server active on `http://localhost:8000` via `uvicorn app.main:app --reload`.
- [ ] **Frontend Running**: App active on `http://localhost:5173` via `npm run dev`.
- [ ] **Demo Resume Ready**: `docs/demo-resume.md` or synthetic sample PDF ready on desktop.
- [ ] **Browser Clean**: Clear previous session state / start fresh tab at `http://localhost:5173`.
- [ ] **No Personal Data Visible**: Ensure no personal emails, real resumes, or private paths are exposed.
- [ ] **No Secrets Visible**: Ensure `.env`, API keys, or secret environment variables are not displayed on terminal screens.

---

## 2. On-Screen Recording Flow Checklist
- [ ] **Landing Screen**: Show landing header, backend status indicator ("connected"), and upload form.
- [ ] **Resume Upload**: Select synthetic PDF resume, choose `Backend Engineer`, and submit.
- [ ] **Question 1 Generation**: Highlight generated question, topic tag, and difficulty rating.
- [ ] **Interactive Q&A Loop**: Input substantive technical responses for Questions 1 through 5.
- [ ] **Loading Feedback**: Point out real-time evaluation and next-question generation states.
- [ ] **Final Report Dashboard**: Show overall calculated score, recommendation badge, key strengths, areas to improve, executive summary, and expandable question breakdown.
- [ ] **Reset Flow**: Click `Start New Interview` to demonstrate clean reset state.

---

## 3. Post-Recording Verification Checklist
- [ ] Confirm no API keys or credentials were shown in video frames or terminal popups.
- [ ] Verify video audio quality is clear and concise (target duration: 3–5 minutes).
