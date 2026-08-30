import { useState, useEffect } from 'react';

function App() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [healthDetails, setHealthDetails] = useState<{ status?: string; service?: string } | null>(null);

  const checkHealth = async () => {
    setHealthStatus('checking');
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/health`);
      if (response.ok) {
        const data = await response.json();
        setHealthDetails(data);
        setHealthStatus('connected');
      } else {
        setHealthStatus('error');
      }
    } catch (err) {
      console.error('Failed to connect to backend health check:', err);
      setHealthStatus('error');
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

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
              onClick={checkHealth}
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
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 flex flex-col gap-8">
        {/* Intro */}
        <section className="text-center max-w-2xl mx-auto mt-4">
          <h2 className="text-3xl font-extrabold text-slate-900 mb-3 sm:text-4xl">
            Technical Practice with AI Context
          </h2>
          <p className="text-slate-600 text-base leading-relaxed">
            Conduct AI-powered role-based technical interviews powered by your resume background and role-specific knowledge bases.
          </p>
        </section>

        {/* Backend Status Card if error or details */}
        {healthStatus === 'connected' && healthDetails && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 max-w-xl mx-auto w-full flex items-center justify-between text-xs text-emerald-800">
            <div>
              <span className="font-semibold">Backend Connected:</span> {healthDetails.service}
            </div>
            <span className="bg-emerald-200 px-2 py-0.5 rounded font-mono uppercase text-[10px]">
              {healthDetails.status}
            </span>
          </div>
        )}

        {healthStatus === 'error' && (
          <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 max-w-xl mx-auto w-full flex items-center justify-between text-xs text-rose-800">
            <div>
              <span className="font-semibold">Backend Connection Failed:</span> Make sure backend is running on port 8000.
            </div>
            <button onClick={checkHealth} className="underline text-rose-900 hover:text-rose-700">Retry</button>
          </div>
        )}

        {/* Placeholders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-2">
          {/* Resume Upload Placeholder */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold mb-4">
                1
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-1">Upload Resume</h3>
              <p className="text-sm text-slate-500 mb-4">
                Upload your PDF resume to extract background skills and experiences.
              </p>
            </div>
            <div className="border-2 border-dashed border-slate-200 rounded-lg p-6 text-center bg-slate-50/50">
              <span className="text-xs text-slate-400 font-medium">Resume Upload Placeholder</span>
            </div>
          </div>

          {/* Role Selection Placeholder */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold mb-4">
                2
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-1">Target Role</h3>
              <p className="text-sm text-slate-500 mb-4">
                Select the backend or AI/ML position you are interviewing for.
              </p>
            </div>
            <div className="border border-slate-200 rounded-lg p-3 bg-slate-50 text-center">
              <span className="text-xs text-slate-400 font-medium">Role Selection Placeholder</span>
            </div>
          </div>
        </div>

        {/* Action Placeholder */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm text-center">
          <button 
            disabled 
            className="w-full sm:w-auto px-8 py-3 bg-indigo-600 text-white font-medium rounded-lg opacity-50 cursor-not-allowed text-sm shadow-sm"
          >
            Start Interview (Placeholder)
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-400">
        AI Role-Based Interviewer &bull; MVP Setup
      </footer>
    </div>
  );
}

export default App;
