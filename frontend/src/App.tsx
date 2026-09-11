import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { CandidateDashboard } from './pages/Candidate/CandidateDashboard';
import { RecruiterDashboard } from './pages/Recruiter/RecruiterDashboard';
import { AuthModal } from './pages/Auth/AuthModal';

const MainLayout: React.FC = () => {
  const { role } = useAuth();
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar onOpenAuth={() => setIsAuthOpen(true)} />
      
      <main className="flex-1">
        {role === 'candidate' ? (
          <CandidateDashboard />
        ) : (
          <RecruiterDashboard />
        )}
      </main>

      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>TalentPulse AI Platform © 2026 — Production Full-Stack AI Recruitment Suite</span>
          <div className="flex space-x-4 text-slate-400">
            <span>FastAPI Backend</span>
            <span>•</span>
            <span>React TypeScript</span>
            <span>•</span>
            <span>Pluggable LLM AI Provider</span>
          </div>
        </div>
      </footer>

      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}

export default App;
