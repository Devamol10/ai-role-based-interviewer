import React, { useState, useEffect } from 'react';
import { 
  checkHealth, 
  uploadResume, 
  generateInterviewQuestion, 
  submitAnswer,
  getInterviewReport,
  getInterviewQuestions,
  type GeneratedQuestionResult,
  type InterviewReportResult
} from './services/api';

const SUPPORTED_ROLES = [
  'Backend Engineer',
  'AI/ML Engineer',
  'Data Science / Applied ML'
];

function App() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [healthDetails, setHealthDetails] = useState<{ status?: string; service?: string } | null>(null);

  // Form State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>(SUPPORTED_ROLES[0]);
  
  // Loading & Error States
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState<boolean>(false);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState<boolean>(false);
  const [isLoadingReport, setIsLoadingReport] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  // Interactive Interview State
  const [currentQuestion, setCurrentQuestion] = useState<GeneratedQuestionResult | null>(null);
  const [answerInput, setAnswerInput] = useState<string>('');
  
  // Results State
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [report, setReport] = useState<InterviewReportResult | null>(null);
  const [questionBreakdown, setQuestionBreakdown] = useState<any[]>([]);

  const fetchHealth = async () => {
    setHealthStatus('checking');
    try {
      const data = await checkHealth();
      setHealthDetails(data);
      setHealthStatus('connected');
    } catch (err) {
      console.error('Health check error:', err);
      setHealthStatus('error');
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
        setErrorMessage('Please select a valid PDF file.');
        setSelectedFile(null);
        return;
      }
      setErrorMessage(null);
      setSelectedFile(file);
    }
  };

  const handleStartInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage('Please select a PDF resume before submitting.');
      return;
    }
    if (!selectedRole) {
      setErrorMessage('Please select a target role.');
      return;
    }

    setIsUploading(true);
    setErrorMessage(null);
    setCurrentQuestion(null);
    setIsCompleted(false);
    setReport(null);

    try {
      // Step 1: Upload Resume & Create Candidate
      const uploadRes = await uploadResume(selectedFile, selectedRole);
      setIsUploading(false);

      // Step 2: Generate Question 1
      setIsGeneratingQuestion(true);
      const questionRes = await generateInterviewQuestion(uploadRes.candidate_id);
      setCurrentQuestion(questionRes);
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred.');
    } finally {
      setIsUploading(false);
      setIsGeneratingQuestion(false);
    }
  };

  const loadFinalReport = async (sessionId: number) => {
    setIsLoadingReport(true);
    try {
      const reportRes = await getInterviewReport(sessionId);
      setReport(reportRes);

      const qsRes = await getInterviewQuestions(sessionId);
      if (qsRes && qsRes.questions) {
        setQuestionBreakdown(qsRes.questions);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate interview report.');
    } finally {
      setIsLoadingReport(false);
    }
  };

  const handleAnswerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentQuestion) return;
    
    const trimmedAnswer = answerInput.trim();
    if (!trimmedAnswer) {
      setErrorMessage('Please enter a substantive answer before submitting.');
      return;
    }

    setIsSubmittingAnswer(true);
    setErrorMessage(null);

    try {
      const result = await submitAnswer(
        currentQuestion.session_id,
        currentQuestion.id,
        trimmedAnswer
      );

      setAnswerInput('');

      if (result.interview_completed) {
        setIsCompleted(true);
        setCurrentQuestion(null);
        await loadFinalReport(result.session_id);
      } else if (result.next_question) {
        setCurrentQuestion(result.next_question);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit answer.');
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 py-4 px-6 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg">
              AI
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              AI Role-Based Interviewer
            </h1>
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={fetchHealth}
              className="text-xs font-medium text-slate-500 hover:text-indigo-600 transition"
            >
              Check Status
            </button>
            <span className="flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-full border border-slate-200 bg-slate-50">
              <span className={`w-2 h-2 rounded-full ${
                healthStatus === 'connected' ? 'bg-emerald-500' :
                healthStatus === 'error' ? 'bg-rose-500' : 'bg-amber-500 animate-pulse'
              }`} />
              <span className="capitalize">{healthStatus}</span>
              {healthDetails?.service && <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">({healthDetails.service})</span>}
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-8 flex flex-col gap-6">
        {/* State 1: Upload & Initial Setup */}
        {!currentQuestion && !isCompleted && (
          <>
            <section className="text-center max-w-2xl mx-auto mt-2">
              <h2 className="text-3xl font-extrabold text-slate-900 mb-3 sm:text-4xl">
                Personalized Technical Interview
              </h2>
              <p className="text-slate-600 text-base leading-relaxed">
                Upload your resume to start an adaptive 5-question technical interview tailored to your experience and grounded in domain knowledge.
              </p>
            </section>

            <form onSubmit={handleStartInterview} className="bg-white p-6 md:p-8 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col">
                  <label className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-xs flex items-center justify-center font-bold">1</span>
                    Upload PDF Resume
                  </label>
                  <div className="relative border-2 border-dashed border-slate-200 hover:border-indigo-400 transition rounded-lg p-6 text-center bg-slate-50 flex flex-col items-center justify-center gap-2">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <input 
                      type="file" 
                      accept=".pdf,application/pdf"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <span className="text-xs text-slate-600 font-medium">
                      {selectedFile ? selectedFile.name : 'Click or drag PDF file here'}
                    </span>
                    <span className="text-[11px] text-slate-400">PDF up to 5 MB</span>
                  </div>
                </div>

                <div className="flex flex-col">
                  <label className="text-sm font-semibold text-slate-900 mb-2 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-700 text-xs flex items-center justify-center font-bold">2</span>
                    Target Role
                  </label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-3 text-sm bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                  >
                    {SUPPORTED_ROLES.map((role) => (
                      <option key={role} value={role}>
                        {role}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-500 mt-2">
                    Question topics & RAG context will be calibrated specifically for this role.
                  </p>
                </div>
              </div>

              {errorMessage && (
                <div className="bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-lg p-4 flex items-center gap-2">
                  <span className="font-semibold">Error:</span> {errorMessage}
                </div>
              )}

              <button
                type="submit"
                disabled={isUploading || isGeneratingQuestion || !selectedFile}
                className={`w-full py-3.5 px-6 rounded-lg font-medium text-sm text-white shadow-sm transition flex items-center justify-center gap-2 ${
                  isUploading || isGeneratingQuestion || !selectedFile 
                    ? 'bg-slate-300 cursor-not-allowed' 
                    : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800'
                }`}
              >
                {isUploading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Extracting Resume Text...
                  </>
                ) : isGeneratingQuestion ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Querying Knowledge Base & Generating Question 1...
                  </>
                ) : (
                  'Upload Resume & Start Interview'
                )}
              </button>
            </form>
          </>
        )}

        {/* State 2: Interactive Interview Screen */}
        {currentQuestion && !isCompleted && (
          <form onSubmit={handleAnswerSubmit} className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 md:p-8 flex flex-col gap-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-full">
                Question {currentQuestion.question_number} of 5
              </span>
              <div className="flex items-center space-x-3 text-xs text-slate-500">
                <span>Topic: <strong className="text-slate-800">{currentQuestion.topic}</strong></span>
                <span>&bull;</span>
                <span>Difficulty: <strong className="text-amber-600">{currentQuestion.difficulty}</strong></span>
              </div>
            </div>

            <div>
              <h3 className="text-lg md:text-xl font-bold text-slate-900 leading-snug mb-3">
                {currentQuestion.question_text}
              </h3>
              {currentQuestion.reason && (
                <p className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-100 italic">
                  Rationale: {currentQuestion.reason}
                </p>
              )}
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Your Answer
              </label>
              <textarea
                rows={5}
                value={answerInput}
                onChange={(e) => setAnswerInput(e.target.value)}
                placeholder="Type your technical answer here in detail..."
                disabled={isSubmittingAnswer}
                className="w-full border border-slate-300 rounded-lg p-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition disabled:bg-slate-50"
              />
            </div>

            {errorMessage && (
              <div className="bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-lg p-4 flex items-center gap-2">
                <span className="font-semibold">Error:</span> {errorMessage}
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => {
                  setCurrentQuestion(null);
                  setSelectedFile(null);
                  setAnswerInput('');
                  setErrorMessage(null);
                }}
                className="text-xs text-slate-500 hover:text-slate-700 font-medium"
              >
                Cancel Interview
              </button>
              <button
                type="submit"
                disabled={isSubmittingAnswer || !answerInput.trim()}
                className={`px-6 py-2.5 rounded-lg font-medium text-sm text-white shadow-sm transition flex items-center gap-2 ${
                  isSubmittingAnswer || !answerInput.trim()
                    ? 'bg-slate-300 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800'
                }`}
              >
                {isSubmittingAnswer ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Evaluating Answer & Generating Next Step...
                  </>
                ) : (
                  'Submit Answer \u2192'
                )}
              </button>
            </div>
          </form>
        )}

        {/* State 3: Loading Report State */}
        {isCompleted && isLoadingReport && (
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-12 text-center flex flex-col items-center justify-center gap-4">
            <svg className="animate-spin h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <h3 className="text-lg font-bold text-slate-900">Evaluating Final Answer & Generating Report...</h3>
            <p className="text-xs text-slate-500">Aggregating scores, strengths, weaknesses, and executive recommendation.</p>
          </div>
        )}

        {/* State 4: Final Results Screen */}
        {isCompleted && !isLoadingReport && !report && errorMessage && (
          <div className="bg-white rounded-xl border border-rose-200 shadow-sm p-10 text-center flex flex-col items-center gap-4">
            <div className="text-rose-500 text-4xl">⚠</div>
            <h3 className="text-lg font-bold text-slate-900">Report Could Not Be Generated</h3>
            <p className="text-sm text-rose-700 bg-rose-50 border border-rose-200 rounded-lg px-4 py-3 max-w-lg">{errorMessage}</p>
            <button
              onClick={() => {
                setIsCompleted(false);
                setCurrentQuestion(null);
                setSelectedFile(null);
                setAnswerInput('');
                setErrorMessage(null);
                setReport(null);
              }}
              className="mt-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg text-sm transition"
            >
              Start New Interview
            </button>
          </div>
        )}

        {/* State 5: Final Results Screen */}
        {isCompleted && !isLoadingReport && report && (
          <div className="flex flex-col gap-6">
            {/* Overall Score Header Card */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex flex-col gap-1 text-center md:text-left">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Interview Completed</span>
                <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900">{selectedRole}</h2>
                <p className="text-xs text-slate-500">Evaluated across 5 RAG-grounded technical questions</p>
              </div>

              <div className="flex items-center gap-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div className="text-center">
                  <span className="text-xs font-semibold text-slate-500 block uppercase">Overall Score</span>
                  <span className="text-3xl font-black text-indigo-600">{report.overall_score} <span className="text-sm font-normal text-slate-400">/ 10</span></span>
                </div>
                <div className="h-10 w-px bg-slate-200" />
                <div className="text-center">
                  <span className="text-xs font-semibold text-slate-500 block uppercase">Recommendation</span>
                  <span className={`text-sm font-bold px-3 py-1 rounded-full inline-block mt-1 ${
                    report.recommendation === 'Strong Candidate' ? 'bg-emerald-100 text-emerald-800' :
                    report.recommendation === 'Good Candidate' ? 'bg-indigo-100 text-indigo-800' :
                    report.recommendation === 'Needs Improvement' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                  }`}>
                    {report.recommendation}
                  </span>
                </div>
              </div>
            </div>

            {/* Strengths & Areas to Improve Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2 text-emerald-600">
                  <span>✓</span> Key Strengths
                </h3>
                <ul className="space-y-2">
                  {report.strengths.map((str, idx) => (
                    <li key={idx} className="text-xs text-slate-700 bg-emerald-50/50 border border-emerald-100 p-2.5 rounded-lg flex items-start gap-2">
                      <span className="text-emerald-500 font-bold">•</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2 text-amber-600">
                  <span>•</span> Areas to Improve
                </h3>
                <ul className="space-y-2">
                  {report.weaknesses.map((wk, idx) => (
                    <li key={idx} className="text-xs text-slate-700 bg-amber-50/50 border border-amber-100 p-2.5 rounded-lg flex items-start gap-2">
                      <span className="text-amber-500 font-bold">•</span>
                      <span>{wk}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Executive Summary Card */}
            <div className="bg-white p-6 md:p-8 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-2">Executive Summary</h3>
              <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200">
                {report.summary}
              </p>
            </div>

            {/* Question Breakdown List */}
            <div className="bg-white p-6 md:p-8 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-4">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Per-Question Evaluation Breakdown</h3>
              <div className="space-y-4">
                {questionBreakdown.map((q, idx) => (
                  <details key={q.id || idx} className="group bg-slate-50 border border-slate-200 rounded-lg p-4 transition">
                    <summary className="flex items-center justify-between cursor-pointer list-none">
                      <div className="flex items-center space-x-3">
                        <span className="w-6 h-6 rounded-full bg-slate-200 text-slate-700 text-xs flex items-center justify-center font-bold">
                          {q.question_number}
                        </span>
                        <span className="text-sm font-semibold text-slate-900">{q.topic}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-xs font-bold px-2.5 py-1 rounded bg-indigo-100 text-indigo-800">
                          {q.score !== null ? `${q.score} / 10` : 'Evaluated'}
                        </span>
                        <span className="text-xs text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                      </div>
                    </summary>

                    <div className="mt-4 pt-4 border-t border-slate-200 space-y-3 text-xs">
                      <div>
                        <span className="font-semibold text-slate-500 block mb-1">Question:</span>
                        <p className="text-slate-900 font-medium">{q.question_text}</p>
                      </div>
                      {q.answer_text && (
                        <div>
                          <span className="font-semibold text-slate-500 block mb-1">Your Answer:</span>
                          <p className="text-slate-800 bg-white p-3 rounded border border-slate-200 whitespace-pre-wrap">{q.answer_text}</p>
                        </div>
                      )}
                      {q.feedback && (
                        <div>
                          <span className="font-semibold text-slate-500 block mb-1">AI Feedback:</span>
                          <p className="text-indigo-900 bg-indigo-50/60 p-3 rounded border border-indigo-100">{q.feedback}</p>
                        </div>
                      )}
                    </div>
                  </details>
                ))}
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex justify-center pt-2">
              <button
                onClick={() => {
                  setIsCompleted(false);
                  setCurrentQuestion(null);
                  setSelectedFile(null);
                  setAnswerInput('');
                  setErrorMessage(null);
                  setReport(null);
                }}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg text-sm transition shadow-sm"
              >
                Start New Interview
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-400">
        AI Role-Based Interviewer &bull; Complete Evaluation & Final Report Flow
      </footer>
    </div>
  );
}

export default App;
