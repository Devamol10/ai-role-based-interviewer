import React, { useState, useEffect } from 'react';
import { checkHealth, uploadResume, type ResumeUploadResult } from './services/api';

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
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<ResumeUploadResult | null>(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
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
    setUploadResult(null);

    try {
      const result = await uploadResume(selectedFile, selectedRole);
      setUploadResult(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred during upload.');
    } finally {
      setIsUploading(false);
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
        {/* Intro */}
        <section className="text-center max-w-2xl mx-auto mt-2">
          <h2 className="text-3xl font-extrabold text-slate-900 mb-3 sm:text-4xl">
            Technical Practice with AI Context
          </h2>
          <p className="text-slate-600 text-base leading-relaxed">
            Upload your resume and select a target engineering position to begin a context-aware technical evaluation.
          </p>
        </section>

        {/* Form Container */}
        <form onSubmit={handleSubmit} className="bg-white p-6 md:p-8 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 1. Resume Upload */}
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

            {/* 2. Role Selection */}
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
                The AI will calibrate question domain & depth according to this role.
              </p>
            </div>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="bg-rose-50 border border-rose-200 text-rose-800 text-sm rounded-lg p-4 flex items-center gap-2">
              <span className="font-semibold">Error:</span> {errorMessage}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isUploading || !selectedFile}
            className={`w-full py-3.5 px-6 rounded-lg font-medium text-sm text-white shadow-sm transition flex items-center justify-center gap-2 ${
              isUploading || !selectedFile 
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
                Processing & Extracting Resume...
              </>
            ) : (
              'Upload Resume & Start Interview'
            )}
          </button>
        </form>

        {/* Upload Success State */}
        {uploadResult && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 shadow-sm flex flex-col gap-3">
            <div className="flex items-center space-x-2 text-emerald-800 font-semibold text-base">
              <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>{uploadResult.message}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs bg-white p-4 rounded-lg border border-emerald-100 text-slate-700">
              <div>
                <span className="font-semibold text-slate-500 block">Candidate ID:</span>
                <span className="font-mono text-slate-900">{uploadResult.candidate_id}</span>
              </div>
              <div>
                <span className="font-semibold text-slate-500 block">Target Role:</span>
                <span className="font-medium text-slate-900">{uploadResult.selected_role}</span>
              </div>
              <div>
                <span className="font-semibold text-slate-500 block">Extracted Text Length:</span>
                <span className="font-mono text-slate-900">{uploadResult.extracted_text_length} characters</span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-400">
        AI Role-Based Interviewer &bull; Step 2 MVP
      </footer>
    </div>
  );
}

export default App;
