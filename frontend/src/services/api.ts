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
  reason: string;
  retrieved_context: RAGChunkResult[];
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
