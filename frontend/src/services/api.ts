const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface HealthResponse {
  status: string;
  service: string;
}

export interface ResumeUploadResult {
  candidate_id: number;
  filename: string;
  selected_role: string;
  extracted_text_length: number;
  message: string;
}

export interface RAGChunkResult {
  text: string;
  source: string;
  role: string;
  chunk_index: number;
}

export interface RAGSearchResponse {
  query: string;
  role: string;
  result_count: number;
  results: RAGChunkResult[];
}

export interface GeneratedQuestionResult {
  id: number;
  session_id: number;
  question_number: number;
  question_text: string;
  topic: string;
  difficulty: string;
  reason?: string;
  retrieved_context: RAGChunkResult[];
}

export interface AnswerSubmitResult {
  message: string;
  session_id: number;
  question_id: number;
  next_question_number: number | null;
  interview_completed: boolean;
  next_question?: GeneratedQuestionResult | null;
}

export interface InterviewSessionState {
  session_id: number;
  candidate_id: number;
  status: string;
  current_question_number: number;
  total_questions: number;
  current_question: GeneratedQuestionResult | null;
  answer_submitted: boolean;
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

export async function generateInterviewQuestion(candidateId: number, topic?: string): Promise<GeneratedQuestionResult> {
  const response = await fetch(`${API_BASE_URL}/api/interview/questions/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ candidate_id: candidateId, topic }),
  });
  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'Failed to generate interview question.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }
  return data as GeneratedQuestionResult;
}

export async function submitAnswer(sessionId: number, questionId: number, answerText: string): Promise<AnswerSubmitResult> {
  const response = await fetch(`${API_BASE_URL}/api/interview/${sessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question_id: questionId, answer_text: answerText }),
  });
  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'Failed to submit answer.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }
  return data as AnswerSubmitResult;
}

export async function getInterview(sessionId: number): Promise<InterviewSessionState> {
  const response = await fetch(`${API_BASE_URL}/api/interview/${sessionId}`);
  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'Failed to fetch interview session.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }
  return data as InterviewSessionState;
}

export async function getInterviewQuestions(sessionId: number): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/interview/${sessionId}/questions`);
  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'Failed to fetch interview questions.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }
  return data;
}

export async function searchRAG(query: string, role: string, topK: number = 5): Promise<RAGSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/rag/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, role, top_k: topK }),
  });
  const data = await response.json();
  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'RAG search request failed.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }
  return data as RAGSearchResponse;
}

export async function uploadResume(file: File, role: string): Promise<ResumeUploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('role', role);

  const response = await fetch(`${API_BASE_URL}/api/resume/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    const errorMsg = data.detail || data.message || 'Failed to upload resume.';
    throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
  }

  return data as ResumeUploadResult;
}
