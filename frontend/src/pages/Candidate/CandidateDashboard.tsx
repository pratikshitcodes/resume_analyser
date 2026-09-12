import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import type { ResumeData, QuestionSet, MockInterviewSession, InterviewSlot } from '../../types';
import { 
  FileText, Upload, Sparkles, CheckCircle2, AlertCircle, 
  Send, MessageSquare, Target, Award, Mic, Play, 
  ChevronRight, Calendar, ExternalLink, RefreshCw, Star, Code2, Zap
} from 'lucide-react';

import { useAuth } from '../../context/AuthContext';

interface CandidateDashboardProps {
  onOpenAuth?: () => void;
}

export const CandidateDashboard: React.FC<CandidateDashboardProps> = ({ onOpenAuth }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'ats' | 'chat' | 'match' | 'interview' | 'slots'>('ats');
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Chat State
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string; sources?: string[] }>>([
    { role: 'assistant', content: 'Hello! I am your AI Career Advisor. I have analyzed your resume and ATS metrics. Ask me anything about tailoring your projects, improving your score, or targeting specific engineering roles!' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  // JD Match State
  const [targetJdText, setTargetJdText] = useState('');
  const [matchResult, setMatchResult] = useState<any>(null);
  const [isMatching, setIsMatching] = useState(false);

  // Mock Interview State
  const [mockSession, setMockSession] = useState<MockInterviewSession | null>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [questionSet, setQuestionSet] = useState<QuestionSet | null>(null);

  // Slots State
  const [availableSlots, setAvailableSlots] = useState<InterviewSlot[]>([]);
  const [isLoadingSlots, setIsLoadingSlots] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadLatestResume();
    } else {
      setResumeData(null);
      setMockSession(null);
      setMatchResult(null);
    }
    loadSlots();
  }, [user]);

  const loadLatestResume = async () => {
    try {
      const res = await api.getLatestResume();
      if (res.data) {
        setResumeData(res.data);
      } else {
        setResumeData(null);
      }
    } catch (err) {
      console.error('Failed to load resume', err);
      setResumeData(null);
    }
  };

  const loadSlots = async () => {
    setIsLoadingSlots(true);
    try {
      const res = await api.getAvailableSlots();
      setAvailableSlots(res.data);
    } catch (err) {
      console.error('Failed to load slots', err);
    } finally {
      setIsLoadingSlots(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!user) {
      onOpenAuth?.();
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.uploadResume(formData);
      setResumeData(res.data);
      loadQuestions();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to upload and parse resume.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSampleResume = async () => {
    if (!user) {
      onOpenAuth?.();
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    const sampleContent = `Alex Johnson
alex.johnson@techmail.com | +1 (555) 382-9912 | linkedin.com/in/alexjohnson-dev | github.com/alexjohnson

PROFESSIONAL SUMMARY
Senior Full Stack & AI Systems Engineer with 3+ years of experience designing high-throughput distributed microservices, REST APIs with FastAPI, and dynamic web interfaces with React and Tailwind CSS.

CORE SKILLS
Python, FastAPI, React, TypeScript, PostgreSQL, SQLAlchemy, Redis, Docker, Git, LLM Prompt Engineering, Celery, REST APIs

PROFESSIONAL EXPERIENCE
Software Engineer — CloudSphere Solutions (2023 - Present)
- Engineered high-throughput microservices using FastAPI and PostgreSQL handling 5,000 requests/sec with under 40ms p95 latency.
- Built asynchronous batch processing pipelines utilizing Redis and Celery, cutting data ingestion duration by 65%.
- Collaborated in cross-functional agile teams to deliver end-to-end features with 95% unit test coverage.

KEY PROJECTS
AI Recruitment & Mock Interview Platform
- Designed full-stack AI evaluation platform with automated resume parsing, ATS scoring, and interactive simulated interviews.
- Integrated LLM structured outputs with strict Pydantic validation and resilient fallback providers.
- Deployed React + Tailwind UI with real-time candidate search and multi-format PDF/CSV export.

Distributed Task Queue Dashboard
- Built real-time telemetry monitoring dashboard for Redis workers using WebSockets and React.

EDUCATION & CERTIFICATIONS
B.S. in Computer Science — California Institute of Technology (2023) — CGPA: 3.9
AWS Certified Solutions Architect — Associate (2024)`;

    const blob = new Blob([sampleContent], { type: 'text/plain' });
    const file = new File([blob], 'Alex_Johnson_FullStack_Resume.txt', { type: 'text/plain' });
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.uploadResume(formData);
      setResumeData(res.data);
      loadQuestions();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to load sample resume.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendChat = async () => {
    if (!chatInput.trim() || isChatLoading) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setIsChatLoading(true);

    try {
      const res = await api.candidateChat({ message: msg });
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: res.data.reply, sources: res.data.context_sources }
      ]);
    } catch (err) {
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an issue retrieving grounded insights. Please try again.' }
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleMatchJD = async () => {
    if (!targetJdText.trim() || isMatching) return;
    setIsMatching(true);
    const formData = new FormData();
    formData.append('jd_text', targetJdText);

    try {
      const res = await api.evaluateJDFit(formData);
      setMatchResult(res.data);
    } catch (err) {
      console.error('Failed to match JD', err);
    } finally {
      setIsMatching(false);
    }
  };

  const loadQuestions = async () => {
    try {
      const res = await api.getInterviewQuestions();
      setQuestionSet(res.data);
    } catch (err) {
      console.error('Failed to generate questions', err);
    }
  };

  const startMock = async () => {
    try {
      const res = await api.startMockInterview({ num_questions: 3 });
      setMockSession(res.data);
      setCurrentQuestionIdx(0);
      setUserAnswer('');
    } catch (err) {
      console.error('Failed to start mock interview', err);
    }
  };

  const submitMockAnswer = async () => {
    if (!mockSession || !userAnswer.trim() || isSubmittingAnswer) return;
    setIsSubmittingAnswer(true);

    try {
      const res = await api.stepMockInterview({
        session_id: mockSession.id,
        question_index: currentQuestionIdx,
        user_answer: userAnswer
      });

      const updated = await api.getMockInterviewSession(mockSession.id);
      setMockSession(updated.data);
      setUserAnswer('');

      if (!res.data.is_completed) {
        setCurrentQuestionIdx(prev => prev + 1);
      }
    } catch (err) {
      console.error('Failed to submit step', err);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleBookSlot = async (slotId: string) => {
    try {
      await api.bookSlot(slotId);
      setBookingSuccess('Interview slot confirmed! An invitation has been added to your calendar.');
      loadSlots();
      setTimeout(() => setBookingSuccess(null), 5000);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to book slot.');
    }
  };

  const atsScore = resumeData?.ats_analysis?.ats_score || 0;
  const scoreColor = atsScore >= 80 ? 'text-emerald-400' : atsScore >= 60 ? 'text-amber-400' : 'text-rose-400';
  const scoreBg = atsScore >= 80 ? 'bg-emerald-500/10 border-emerald-500/20' : atsScore >= 60 ? 'bg-amber-500/10 border-amber-500/20' : 'bg-rose-500/10 border-rose-500/20';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-indigo-900/40 via-slate-900 to-slate-900 border border-indigo-500/20 mb-8 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Candidate Workspace</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            {resumeData?.profile?.name ? `Welcome back, ${resumeData.profile.name}` : 'AI Career & Interview Studio'}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Analyze your ATS score, simulate real-time AI technical interviews, and match against target job descriptions.
          </p>
        </div>

        {/* Quick Upload Action */}
        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold cursor-pointer shadow-lg shadow-indigo-600/30 transition-all">
            <Upload className="w-4 h-4" />
            <span>{isUploading ? 'Analyzing Resume...' : 'Upload New Resume'}</span>
            <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" disabled={isUploading} />
          </label>
          {!resumeData && (
            <button
              onClick={handleSampleResume}
              disabled={isUploading}
              className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs sm:text-sm font-medium border border-slate-700 transition-colors"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Load Sample Resume</span>
            </button>
          )}
        </div>
      </div>

      {uploadError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center space-x-2 mb-6">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{uploadError}</span>
        </div>
      )}

      {bookingSuccess && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex items-center space-x-2 mb-6">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          <span>{bookingSuccess}</span>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'ats', label: 'ATS Analysis & Profile', icon: Award },
          { id: 'chat', label: 'AI Career Copilot (RAG)', icon: MessageSquare },
          { id: 'match', label: 'Target JD Matcher', icon: Target },
          { id: 'interview', label: 'Mock Interview Studio', icon: Mic },
          { id: 'slots', label: 'Interview Slots', icon: Calendar },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: ATS Analysis & Profile */}
      {activeTab === 'ats' && (
        <div className="space-y-8">
          {!resumeData ? (
            <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-slate-800 bg-slate-900/30">
              <FileText className="w-12 h-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-200">No Resume Uploaded Yet</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mt-1 mb-6">
                Upload your resume in PDF, DOCX, or TXT format to compute your ATS score, extract structured skills, and simulate interviews.
              </p>
              <div className="flex justify-center gap-3">
                <label className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium cursor-pointer shadow-lg shadow-indigo-600/25">
                  <Upload className="w-4 h-4" />
                  <span>Upload Resume</span>
                  <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileUpload} className="hidden" />
                </label>
                <button
                  onClick={handleSampleResume}
                  className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700"
                >
                  <Zap className="w-4 h-4 text-amber-400" />
                  <span>Use Sample Full Stack Resume</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* ATS Score & Best Project Column */}
              <div className="space-y-6">
                
                {/* ATS Score Gauge Card */}
                <div className={`p-6 rounded-2xl border ${scoreBg} backdrop-blur-sm relative overflow-hidden shadow-lg`}>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">ATS Match Score</span>
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-900/80 border border-slate-700 text-slate-200">
                      {atsScore >= 80 ? 'Highly Competitive' : atsScore >= 60 ? 'Moderate Fit' : 'Needs Optimization'}
                    </span>
                  </div>

                  <div className="flex items-center justify-center py-4">
                    <div className="relative w-36 h-36 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                        <path
                          className="text-slate-800"
                          strokeWidth="3.5"
                          stroke="currentColor"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path
                          className={scoreColor}
                          strokeDasharray={`${atsScore}, 100`}
                          strokeWidth="3.5"
                          strokeLinecap="round"
                          stroke="currentColor"
                          fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center">
                        <span className={`text-3xl font-extrabold ${scoreColor}`}>{atsScore}</span>
                        <span className="text-[10px] text-slate-400 uppercase font-medium">out of 100</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 text-center mt-2">
                    Evaluated across keyword density, quantifiable metrics, section hierarchy, and modern schema standards.
                  </p>
                </div>

                {/* Best Project Spotlight Card */}
                {resumeData.ats_analysis?.best_project_analysis && (
                  <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-lg">
                    <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-2">
                      <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                      <span>Best Project Impact Analysis</span>
                    </div>
                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      {resumeData.ats_analysis.best_project_analysis}
                    </p>
                  </div>
                )}

                {/* Contact & Links */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Candidate Metadata</h4>
                  <div className="space-y-2 text-xs text-slate-300">
                    <div className="flex justify-between py-1 border-b border-slate-800/60">
                      <span className="text-slate-500">Full Name</span>
                      <span className="font-medium text-slate-200">{resumeData.profile?.name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/60">
                      <span className="text-slate-500">Email</span>
                      <span className="font-medium text-slate-200">{resumeData.profile?.contact_info?.email || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-800/60">
                      <span className="text-slate-500">Total Exp</span>
                      <span className="font-medium text-slate-200">{resumeData.profile?.total_experience_years || 0} Years</span>
                    </div>
                    {resumeData.profile?.contact_info?.github && (
                      <div className="flex justify-between py-1 border-b border-slate-800/60">
                        <span className="text-slate-500">GitHub</span>
                        <a href={resumeData.profile.contact_info.github} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline truncate max-w-[150px]">
                          {resumeData.profile.contact_info.github}
                        </a>
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* Strengths, Weaknesses, and Detailed Profile */}
              <div className="lg:col-span-2 space-y-6">
                
                {/* Strengths & Weaknesses Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-5 rounded-2xl bg-slate-900/80 border border-emerald-500/20 shadow-sm">
                    <div className="flex items-center space-x-2 text-emerald-400 text-xs font-bold uppercase tracking-wider mb-3">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Key Resume Strengths</span>
                    </div>
                    <ul className="space-y-2">
                      {resumeData.ats_analysis?.strengths?.map((s, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0"></span>
                          <span>{s}</span>
                        </li>
                      )) || <li className="text-xs text-slate-500">No specific strengths generated.</li>}
                    </ul>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-900/80 border border-amber-500/20 shadow-sm">
                    <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-3">
                      <AlertCircle className="w-4 h-4" />
                      <span>Gaps & Improvements</span>
                    </div>
                    <ul className="space-y-2">
                      {resumeData.ats_analysis?.suggestions?.map((s, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0"></span>
                          <span>{s}</span>
                        </li>
                      )) || <li className="text-xs text-slate-500">No suggestions needed.</li>}
                    </ul>
                  </div>
                </div>

                {/* Skills Cloud */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center space-x-2">
                    <Code2 className="w-4 h-4 text-indigo-400" />
                    <span>Extracted Technical Skills</span>
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.profile?.skills?.map((skill, idx) => (
                      <span key={idx} className="px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 text-indigo-300 border border-slate-700/80">
                        {skill}
                      </span>
                    )) || <span className="text-xs text-slate-500">No skills parsed</span>}
                  </div>
                </div>

                {/* Work Experience */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Work Experience</h4>
                  <div className="space-y-4">
                    {resumeData.profile?.experience?.map((exp, idx) => (
                      <div key={idx} className="border-l-2 border-indigo-500/40 pl-4 py-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-sm font-semibold text-white">{exp.role}</span>
                            <span className="text-xs text-indigo-400 ml-2">@ {exp.company}</span>
                          </div>
                          {exp.duration && <span className="text-xs text-slate-500">{exp.duration}</span>}
                        </div>
                        {exp.description && (
                          <p className="text-xs text-slate-300 mt-1 leading-relaxed">{exp.description}</p>
                        )}
                      </div>
                    )) || <p className="text-xs text-slate-500">No experience records found.</p>}
                  </div>
                </div>

                {/* Projects */}
                <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 shadow-sm">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Projects</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {resumeData.profile?.projects?.map((proj, idx) => (
                      <div key={idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-white">{proj.name}</span>
                            {proj.link && (
                              <a href={proj.link} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300">
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                          </div>
                          <p className="text-xs text-slate-400 line-clamp-3 mb-2">{proj.description}</p>
                        </div>
                        {proj.technologies && proj.technologies.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {proj.technologies.map((t, ti) => (
                              <span key={ti} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )) || <p className="text-xs text-slate-500">No projects parsed.</p>}
                  </div>
                </div>

              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: AI Career Copilot (RAG Chat) */}
      {activeTab === 'chat' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl max-w-4xl mx-auto flex flex-col h-[650px]">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Grounded Career Advisor</h3>
                <span className="text-[10px] text-emerald-400">● Grounded in your parsed resume & ATS data</span>
              </div>
            </div>
            <button
              onClick={() => setChatMessages([{ role: 'assistant', content: 'Chat history reset. How can I assist you with your career and resume optimization today?' }])}
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center space-x-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-2 mb-3">
            {[
              'What roles best match my skills?',
              'How can I boost my ATS score to 95+?',
              'Critique my project descriptions',
              'What interview questions should I expect?'
            ].map((p, i) => (
              <button
                key={i}
                onClick={() => setChatInput(p)}
                className="text-[11px] px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              >
                {p}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-2">
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none shadow-md shadow-indigo-600/20'
                      : 'bg-slate-800/90 text-slate-200 rounded-bl-none border border-slate-700/60 shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-slate-700/60 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] text-indigo-300 font-semibold uppercase">Sources:</span>
                      {msg.sources.map((src, si) => (
                        <span key={si} className="text-[10px] px-2 py-0.5 rounded bg-slate-900/80 text-slate-300 border border-slate-700">
                          {src}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isChatLoading && (
              <div className="flex items-center space-x-2 text-xs text-indigo-400 p-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Generating grounded career insights...</span>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-800 mt-2 flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
              placeholder="Ask about your skills, role readiness, or project improvements..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
            <button
              onClick={handleSendChat}
              disabled={isChatLoading || !chatInput.trim()}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition-colors flex items-center justify-center shadow-md shadow-indigo-600/25"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* TAB 3: Target JD Matcher */}
      {activeTab === 'match' && (
        <div className="space-y-6 max-w-5xl mx-auto">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <h3 className="text-base font-bold text-white mb-2">Job Description Fit Evaluation</h3>
            <p className="text-xs text-slate-400 mb-4">
              Paste a target job posting below to compute your match score, uncover missing technical skills, and review automated classification.
            </p>

            <textarea
              rows={6}
              value={targetJdText}
              onChange={(e) => setTargetJdText(e.target.value)}
              placeholder="Paste Job Description text here..."
              className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />

            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setTargetJdText(`Role: Senior Backend Engineer\nCompany: DataForge AI\nRequirements: 3+ years experience with Python, FastAPI, PostgreSQL, Docker, Redis, and Celery. Strong experience with microservices architecture and high-load distributed systems.`)}
                className="text-xs text-indigo-400 hover:underline"
              >
                + Insert Sample Job Description
              </button>

              <button
                onClick={handleMatchJD}
                disabled={isMatching || !targetJdText.trim()}
                className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold disabled:opacity-50 shadow-lg shadow-indigo-600/25 transition-all"
              >
                {isMatching ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />}
                <span>{isMatching ? 'Analyzing Fit...' : 'Evaluate Resume Fit'}</span>
              </button>
            </div>
          </div>

          {matchResult && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Match Result</span>
                  <h4 className="text-xl font-bold text-white">Target Job Compatibility</h4>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-4 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider ${
                    matchResult.classification === 'shortlist'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                      : matchResult.classification === 'maybe'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  }`}>
                    {matchResult.classification}
                  </span>
                  <span className="text-2xl font-black text-white">{matchResult.match_score}%</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-950 border border-emerald-500/20">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 block">
                    ✓ Matched Skills ({matchResult.matched_skills?.length || 0})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchResult.matched_skills?.map((s: string, idx: number) => (
                      <span key={idx} className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/20">
                  <span className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 block">
                    ⚠ Skill Gaps / Missing ({matchResult.missing_skills?.length || 0})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {matchResult.missing_skills?.length > 0 ? (
                      matchResult.missing_skills.map((s: string, idx: number) => (
                        <span key={idx} className="text-xs px-2.5 py-1 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-medium">
                          {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">None! You meet 100% of required skills.</span>
                    )}
                  </div>
                </div>
              </div>

              {matchResult.ranking_explanation && (
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 block">AI Justification & Evidence</span>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{matchResult.ranking_explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 4: Mock Interview Studio */}
      {activeTab === 'interview' && (
        <div className="space-y-6 max-w-4xl mx-auto">
          {!mockSession ? (
            <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl text-center space-y-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/30">
                <Mic className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">AI Technical Mock Interview</h3>
                <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto mt-1">
                  Practice with questions tailored directly to your projects and tech stack. Receive instant scoring, feedback, and an overall hiring readiness evaluation.
                </p>
              </div>

              <button
                onClick={startMock}
                className="px-8 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all"
              >
                Start Simulated Interview
              </button>

              {questionSet && (
                <div className="mt-8 text-left border-t border-slate-800 pt-6">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Tailored Question Pool</h4>
                  <div className="space-y-2">
                    {questionSet.technical.slice(0, 2).map((q, i) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300">
                        <span className="text-indigo-400 font-semibold mr-2">[Technical]</span>
                        {q}
                      </div>
                    ))}
                    {questionSet.project.slice(0, 1).map((q, i) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300">
                        <span className="text-purple-400 font-semibold mr-2">[Project Depth]</span>
                        {q}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : mockSession.status === 'in_progress' ? (
            <div className="p-6 rounded-2xl bg-slate-900 border border-indigo-500/30 shadow-2xl space-y-6">
              
              <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                  <Play className="w-4 h-4" />
                  <span>Question {currentQuestionIdx + 1} of {mockSession.questions.length}</span>
                </div>
                <div className="flex space-x-1">
                  {mockSession.questions.map((_, qi) => (
                    <div
                      key={qi}
                      className={`w-6 h-1.5 rounded-full ${
                        qi < currentQuestionIdx
                          ? 'bg-emerald-500'
                          : qi === currentQuestionIdx
                          ? 'bg-indigo-500 animate-pulse'
                          : 'bg-slate-800'
                      }`}
                    />
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Interviewer</span>
                <p className="text-base font-semibold text-white mt-1">
                  {mockSession.questions[currentQuestionIdx]}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-400">Your Answer (Type your technical explanation):</label>
                <textarea
                  rows={6}
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  placeholder="Explain your approach, design decisions, and tradeoffs in detail..."
                  className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div className="flex justify-end">
                <button
                  onClick={submitMockAnswer}
                  disabled={isSubmittingAnswer || !userAnswer.trim()}
                  className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold disabled:opacity-50 shadow-lg shadow-indigo-600/25 transition-all"
                >
                  {isSubmittingAnswer ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ChevronRight className="w-4 h-4" />}
                  <span>{isSubmittingAnswer ? 'Evaluating Answer...' : 'Submit & Next Question'}</span>
                </button>
              </div>

              {mockSession.transcript && mockSession.transcript.length > 0 && (
                <div className="pt-6 border-t border-slate-800 space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Live Interview Feedback History</h4>
                  {mockSession.transcript.map((step, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-white">Q{idx + 1}: {step.question}</span>
                        <span className="text-xs font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
                          Score: {step.score}%
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 italic">"{step.answer}"</p>
                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-indigo-300">
                        <b>AI Feedback:</b> {step.feedback}
                      </div>
                    </div>
                  ))}
                </div>
              )}

            </div>
          ) : (
            <div className="p-8 rounded-2xl bg-slate-900 border border-emerald-500/30 shadow-2xl space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Interview Completed</span>
                  <h3 className="text-2xl font-black text-white">Hiring Readiness Scorecard</h3>
                </div>
                <div className="flex items-center space-x-3 p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-xs text-slate-400">Readiness Score:</span>
                  <span className="text-2xl font-black text-emerald-400">{mockSession.readiness_score}%</span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Technical Depth', score: mockSession.scores?.technical || 85 },
                  { label: 'Communication', score: mockSession.scores?.communication || 90 },
                  { label: 'Project Depth', score: mockSession.scores?.projects || 80 },
                  { label: 'Problem Solving', score: mockSession.scores?.problem_solving || 88 },
                ].map((cat, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-center">
                    <span className="text-[11px] font-medium text-slate-400 block mb-1">{cat.label}</span>
                    <span className="text-xl font-bold text-white">{cat.score}%</span>
                  </div>
                ))}
              </div>

              <div className="p-5 rounded-xl bg-slate-950 border border-slate-800">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2 block">Executive Board Feedback</span>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{mockSession.feedback}</p>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={startMock}
                  className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors"
                >
                  Start Another Mock Interview
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: Available Interview Slots */}
      {activeTab === 'slots' && (
        <div className="space-y-6 max-w-4xl mx-auto">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl">
            <h3 className="text-base font-bold text-white mb-2">Book Recruiter Interview Slots</h3>
            <p className="text-xs text-slate-400 mb-6">
              Recruiters publish open interview slots for shortlisted candidates. Pick an available time below to confirm your schedule.
            </p>

            {isLoadingSlots ? (
              <div className="text-center py-12 text-slate-500 text-xs">Loading available slots...</div>
            ) : availableSlots.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
                No open slots published at this moment. Please check back later.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {availableSlots.map(slot => (
                  <div key={slot.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-white block">
                        {new Date(slot.start_time).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                      <span className="text-xs text-indigo-400">
                        {new Date(slot.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(slot.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <button
                      onClick={() => handleBookSlot(slot.id)}
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-sm transition-colors"
                    >
                      Book Slot
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};
