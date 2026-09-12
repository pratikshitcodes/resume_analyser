import React, { useState, useEffect } from 'react';
import { api } from '../../api/client';
import type { Job, RankedCandidate, InterviewSlot, TaskStatus } from '../../types';
import { 
  Briefcase, Plus, Upload, Filter, Search, Download, 
  FileText, Users, ArrowUpDown, 
  Calendar, Send, Sparkles, RefreshCw, Quote
} from 'lucide-react';

import { useAuth } from '../../context/AuthContext';

interface RecruiterDashboardProps {
  onOpenAuth?: () => void;
}

export const RecruiterDashboard: React.FC<RecruiterDashboardProps> = ({ onOpenAuth }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'jobs' | 'batch' | 'rankings' | 'search' | 'slots' | 'exports'>('rankings');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // New Job Form
  const [newJobTitle, setNewJobTitle] = useState('');
  const [newJobCompany, setNewJobCompany] = useState('TechCorp');
  const [newJobDescription, setNewJobDescription] = useState('');
  const [isCreatingJob, setIsCreatingJob] = useState(false);

  // Batch Upload State
  const [batchFiles, setBatchFiles] = useState<FileList | null>(null);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [isUploadingBatch, setIsUploadingBatch] = useState(false);

  // Candidate Rankings State
  const [rankings, setRankings] = useState<RankedCandidate[]>([]);
  const [filterClassification, setFilterClassification] = useState<string>('');
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [isLoadingRankings, setIsLoadingRankings] = useState(false);

  // Recruiter NLQ Chat State
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string; sources?: string[] }>>([
    { role: 'assistant', content: 'Recruiter Copilot online. Ask me to find, filter, or compare candidates from your applicant pool (e.g. "Find candidates with 3+ years experience in Python and PostgreSQL").' }
  ]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Slots State
  const [slots, setSlots] = useState<InterviewSlot[]>([]);
  const [newSlotStart, setNewSlotStart] = useState('');
  const [newSlotEnd, setNewSlotEnd] = useState('');

  useEffect(() => {
    if (user) {
      loadJobs();
    } else {
      setJobs([]);
      setSelectedJobId('');
      setSelectedJob(null);
      setRankings([]);
    }
  }, [user]);

  useEffect(() => {
    if (selectedJobId) {
      const job = jobs.find(j => j.id === selectedJobId) || null;
      setSelectedJob(job);
      loadRankings(selectedJobId, filterClassification);
      loadSlots(selectedJobId);
    }
  }, [selectedJobId, filterClassification]);

  // Polling for active background tasks
  useEffect(() => {
    if (!activeTaskId) return;

    const interval = setInterval(async () => {
      try {
        const res = await api.getTaskStatus(activeTaskId);
        setTaskStatus(res.data);
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          clearInterval(interval);
          if (selectedJobId) loadRankings(selectedJobId);
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeTaskId, selectedJobId]);

  const loadJobs = async () => {
    try {
      const res = await api.getJobs();
      setJobs(res.data);
      if (res.data.length > 0 && !selectedJobId) {
        setSelectedJobId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load jobs', err);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      onOpenAuth?.();
      return;
    }
    if (!newJobTitle.trim() || !newJobDescription.trim()) return;
    setIsCreatingJob(true);

    try {
      const res = await api.createJob({
        title: newJobTitle,
        company: newJobCompany,
        description: newJobDescription,
      });
      setJobs(prev => [res.data, ...prev]);
      setSelectedJobId(res.data.id);
      setNewJobTitle('');
      setNewJobDescription('');
      setActiveTab('rankings');
    } catch (err) {
      console.error('Failed to create job', err);
    } finally {
      setIsCreatingJob(false);
    }
  };

  const loadRankings = async (jobId: string, classification?: string) => {
    setIsLoadingRankings(true);
    try {
      const res = await api.getRankings(jobId, classification || undefined);
      setRankings(res.data);
    } catch (err) {
      console.error('Failed to load rankings', err);
    } finally {
      setIsLoadingRankings(false);
    }
  };

  const loadSlots = async (jobId: string) => {
    try {
      const res = await api.getInterviewSlots(jobId);
      setSlots(res.data);
    } catch (err) {
      console.error('Failed to load slots', err);
    }
  };

  const handleBatchUpload = async () => {
    if (!user) {
      onOpenAuth?.();
      return;
    }
    if (!selectedJobId || !batchFiles || batchFiles.length === 0) return;
    setIsUploadingBatch(true);
    const formData = new FormData();
    for (let i = 0; i < batchFiles.length; i++) {
      formData.append('files', batchFiles[i]);
    }

    try {
      const res = await api.batchUploadResumes(selectedJobId, formData);
      setActiveTaskId(res.data.task_id);
      setTaskStatus({
        task_id: res.data.task_id,
        status: 'processing',
        progress: 10,
        message: 'Uploading and queueing batch resumes...'
      });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Batch upload failed.');
    } finally {
      setIsUploadingBatch(false);
    }
  };

  const handleLoadDemoBatch = async () => {
    if (!user) {
      onOpenAuth?.();
      return;
    }
    if (!selectedJobId) return;
    setIsUploadingBatch(true);

    const resumes = [
      {
        name: 'Sarah_Connor_Senior_Backend.txt',
        content: `Sarah Connor\nsarah@connor.dev | +1 555-0129 | github.com/sconnor\nSummary: 5+ years backend engineer expert in Python, FastAPI, PostgreSQL, and Docker.\nExperience: Senior Backend Developer at CyberTech (2021-Present).\nSkills: Python, FastAPI, PostgreSQL, Docker, Kubernetes, Redis, Celery.\nProjects: Automated Trading Engine (FastAPI/Redis) handling 20,000 req/sec.`
      },
      {
        name: 'David_Miller_FullStack.txt',
        content: `David Miller\ndavid.miller@example.com | github.com/dmiller\nSummary: 3 years building web apps in React, TypeScript, Python, and PostgreSQL.\nExperience: Full Stack Engineer at WebFlow Dynamics (2023-Present).\nSkills: Python, React, TypeScript, FastAPI, PostgreSQL, Tailwind CSS, Git.\nProjects: AI Video Revisor and Search Portal with React and FastAPI.`
      },
      {
        name: 'Elena_Rostova_Junior_Dev.txt',
        content: `Elena Rostova\nelena@codecraft.io\nSummary: Recent CS graduate with passion for web development and modern stacks.\nEducation: B.S. in Computer Science (2024).\nSkills: JavaScript, HTML, CSS, React, basic Python.\nProjects: Portfolio website and simple task manager.`
      }
    ];

    const formData = new FormData();
    resumes.forEach(r => {
      const blob = new Blob([r.content], { type: 'text/plain' });
      formData.append('files', new File([blob], r.name, { type: 'text/plain' }));
    });

    try {
      const res = await api.batchUploadResumes(selectedJobId, formData);
      setActiveTaskId(res.data.task_id);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to queue demo batch.');
    } finally {
      setIsUploadingBatch(false);
    }
  };

  const handleRecruiterChat = async () => {
    if (!selectedJobId || !chatInput.trim() || isChatLoading) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setIsChatLoading(true);

    try {
      const res = await api.recruiterChat(selectedJobId, { message: msg });
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: res.data.reply, sources: res.data.context_sources }
      ]);
    } catch (err) {
      setChatMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I could not complete the candidate query. Please try again.' }
      ]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleCreateSlot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJobId || !newSlotStart || !newSlotEnd) return;

    try {
      const res = await api.createInterviewSlot(selectedJobId, {
        job_id: selectedJobId,
        start_time: newSlotStart,
        end_time: newSlotEnd
      });
      setSlots(prev => [...prev, res.data]);
      setNewSlotStart('');
      setNewSlotEnd('');
    } catch (err) {
      console.error('Failed to create slot', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-emerald-950/50 via-slate-900 to-slate-900 border border-emerald-500/20 mb-8 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Briefcase className="w-4 h-4" />
            <span>Recruiter Workspace</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white">
            Talent Acquisition & Candidate Screening
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Manage job postings, bulk-process applicant resumes asynchronously, and rank talent with evidence-backed justification.
          </p>
        </div>

        {/* Job Selector Dropdown */}
        <div className="flex items-center space-x-3">
          <div className="flex flex-col">
            <label className="text-[10px] uppercase font-bold text-slate-400 mb-1">Active Job Requisition</label>
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="px-4 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs sm:text-sm text-slate-100 focus:outline-none focus:border-emerald-500 transition-colors max-w-[240px]"
            >
              {jobs.map(job => (
                <option key={job.id} value={job.id}>
                  {job.title} ({job.company})
                </option>
              ))}
              {jobs.length === 0 && <option value="">No jobs created yet</option>}
            </select>
          </div>
          <button
            onClick={() => setActiveTab('jobs')}
            className="self-end px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-md shadow-emerald-600/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Job</span>
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'rankings', label: 'Candidate Ranking Matrix', icon: ArrowUpDown },
          { id: 'batch', label: 'Batch Resume Screener', icon: Upload },
          { id: 'search', label: 'Recruiter AI Search (NLQ)', icon: Search },
          { id: 'jobs', label: 'Job Postings & JD Creator', icon: Briefcase },
          { id: 'slots', label: 'Interview Calendar Slots', icon: Calendar },
          { id: 'exports', label: 'Export Reports', icon: Download },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                isActive
                  ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: Candidate Ranking Matrix */}
      {activeTab === 'rankings' && (
        <div className="space-y-6">
          
          {/* Controls & Filter Pills */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Classification Filter:</span>
              <div className="flex space-x-1.5">
                {[
                  { id: '', label: 'All Candidates' },
                  { id: 'shortlist', label: 'Shortlist' },
                  { id: 'maybe', label: 'Maybe' },
                  { id: 'reject', label: 'Reject' },
                ].map(f => (
                  <button
                    key={f.id}
                    onClick={() => setFilterClassification(f.id)}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                      filterClassification === f.id
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-3 text-xs text-slate-400">
              <span>Total Screened: <b className="text-white">{rankings.length}</b></span>
              <button
                onClick={() => selectedJobId && loadRankings(selectedJobId, filterClassification)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Rankings Table */}
          {isLoadingRankings ? (
            <div className="text-center py-16 text-xs text-slate-500">Loading candidate matrix...</div>
          ) : rankings.length === 0 ? (
            <div className="text-center py-16 px-4 rounded-2xl border-2 border-dashed border-slate-800 bg-slate-900/30">
              <Users className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-base font-semibold text-slate-200">No Candidates Screened Yet</h3>
              <p className="text-slate-400 text-xs max-w-md mx-auto mt-1 mb-4">
                Upload candidate resumes via the Batch Screener to generate weighted rankings and evidence-based fit analysis.
              </p>
              <button
                onClick={() => setActiveTab('batch')}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
              >
                Go to Batch Screener
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900/80 shadow-xl">
              <table className="w-full text-left text-xs sm:text-sm">
                <thead className="bg-slate-950 text-slate-400 text-[11px] uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3.5 px-4">Rank</th>
                    <th className="py-3.5 px-4">Candidate</th>
                    <th className="py-3.5 px-4">Match Score</th>
                    <th className="py-3.5 px-4">Classification</th>
                    <th className="py-3.5 px-4">Matched Core Skills</th>
                    <th className="py-3.5 px-4">Experience</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {rankings.map(cand => (
                    <tr key={cand.match_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-4 px-4 font-extrabold text-slate-300">#{cand.rank}</td>
                      <td className="py-4 px-4">
                        <span className="font-semibold text-white block">{cand.candidate_name}</span>
                        <span className="text-xs text-slate-500">{cand.candidate_email}</span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-white text-base">{cand.match_score}%</span>
                          <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                cand.match_score >= 80 ? 'bg-emerald-500' : cand.match_score >= 60 ? 'bg-amber-500' : 'bg-rose-500'
                              }`}
                              style={{ width: `${cand.match_score}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider ${
                          cand.classification === 'shortlist'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : cand.classification === 'maybe'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}>
                          {cand.classification}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex flex-wrap gap-1 max-w-[220px]">
                          {cand.matched_skills.slice(0, 3).map((s, si) => (
                            <span key={si} className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                              {s}
                            </span>
                          ))}
                          {cand.matched_skills.length > 3 && (
                            <span className="text-[10px] text-slate-500">+{cand.matched_skills.length - 3}</span>
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4 text-slate-300 font-medium">{cand.total_experience_years} Yrs</td>
                      <td className="py-4 px-4 text-right">
                        <button
                          onClick={() => setSelectedCandidate(cand)}
                          className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-colors"
                        >
                          View Evidence
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Evidence Deep Dive Modal */}
          {selectedCandidate && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl relative">
                <div className="flex justify-between items-start pb-4 border-b border-slate-800">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Rank #{selectedCandidate.rank} Evaluation</span>
                    <h3 className="text-xl font-bold text-white mt-0.5">{selectedCandidate.candidate_name}</h3>
                    <span className="text-xs text-slate-400">{selectedCandidate.candidate_email}</span>
                  </div>
                  <button
                    onClick={() => setSelectedCandidate(null)}
                    className="text-slate-400 hover:text-white text-sm p-1"
                  >
                    ✕
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Match Score</span>
                    <span className="text-lg font-bold text-emerald-400">{selectedCandidate.match_score}%</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Total Experience</span>
                    <span className="text-lg font-bold text-white">{selectedCandidate.total_experience_years} Years</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Ranking Explanation</span>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{selectedCandidate.ranking_explanation}</p>
                </div>

                {selectedCandidate.evidence_quotes && selectedCandidate.evidence_quotes.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                      <Quote className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Citing Direct Resume Evidence</span>
                    </span>
                    <div className="space-y-2">
                      {selectedCandidate.evidence_quotes.map((q, qi) => (
                        <div key={qi} className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 text-xs text-indigo-200 italic">
                          "{q}"
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-end pt-2">
                  <button
                    onClick={() => setSelectedCandidate(null)}
                    className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

      {/* TAB 2: Batch Resume Screener */}
      {activeTab === 'batch' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
            <div>
              <h3 className="text-base font-bold text-white">Asynchronous Batch Resume Screener</h3>
              <p className="text-xs text-slate-400 mt-1">
                Upload hundreds of candidate resumes at once (multiple PDF/DOCX files or a ZIP archive). The native background queue will process, extract, and match each candidate asynchronously.
              </p>
            </div>

            <div className="border-2 border-dashed border-slate-800 hover:border-emerald-500/50 p-8 rounded-2xl bg-slate-950/60 text-center space-y-4 transition-colors">
              <Upload className="w-10 h-10 text-emerald-400 mx-auto" />
              <div>
                <span className="text-sm font-semibold text-slate-200 block">Select multiple resumes or a ZIP archive</span>
                <span className="text-xs text-slate-500">Supports .pdf, .docx, .txt, .zip</span>
              </div>

              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.zip"
                onChange={(e) => setBatchFiles(e.target.files)}
                className="block mx-auto text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-emerald-600 file:text-white hover:file:bg-emerald-500 cursor-pointer"
              />

              {batchFiles && batchFiles.length > 0 && (
                <div className="text-xs text-emerald-400 font-medium">
                  ✓ {batchFiles.length} file(s) selected
                </div>
              )}
            </div>

            <div className="flex justify-between items-center pt-2">
              <button
                onClick={handleLoadDemoBatch}
                disabled={isUploadingBatch || !selectedJobId}
                className="text-xs text-slate-400 hover:text-slate-200 border border-slate-800 px-4 py-2 rounded-xl bg-slate-950"
              >
                Load Demo Applicant Pool (3 Candidates)
              </button>

              <button
                onClick={handleBatchUpload}
                disabled={isUploadingBatch || !batchFiles || batchFiles.length === 0 || !selectedJobId}
                className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs sm:text-sm font-semibold disabled:opacity-50 shadow-lg shadow-emerald-600/25 transition-all"
              >
                {isUploadingBatch ? 'Queueing Batch...' : 'Start Asynchronous Screening'}
              </button>
            </div>

            {taskStatus && (
              <div className="p-5 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-3 mt-6">
                <div className="flex justify-between items-center text-xs">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${taskStatus.status === 'processing' ? 'animate-spin' : ''}`} />
                    <span className="font-semibold text-white">Status: {taskStatus.status.toUpperCase()}</span>
                  </div>
                  <span className="font-bold text-emerald-400">{taskStatus.progress}%</span>
                </div>

                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300"
                    style={{ width: `${taskStatus.progress}%` }}
                  />
                </div>

                <p className="text-xs text-slate-400">{taskStatus.message}</p>
              </div>
            )}

          </div>
        </div>
      )}

      {/* TAB 3: Recruiter AI Search (NLQ) */}
      {activeTab === 'search' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl max-w-4xl mx-auto flex flex-col h-[650px]">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Recruiter Natural Language Query Engine</h3>
                <span className="text-[10px] text-slate-400">Query your applicant database in plain English</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-3">
            {[
              'Show me top candidates with 3+ years experience in Python',
              'Who has experience with Docker and distributed systems?',
              'Compare the top 2 candidates',
              'Summarize the applicant pool strengths'
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
                      ? 'bg-emerald-600 text-white rounded-br-none shadow-md shadow-emerald-600/20'
                      : 'bg-slate-800/90 text-slate-200 rounded-bl-none border border-slate-700/60 shadow-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-slate-700/60 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] text-emerald-300 font-semibold uppercase">Citations:</span>
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
              <div className="flex items-center space-x-2 text-xs text-emerald-400 p-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Searching applicant database...</span>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-800 mt-2 flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleRecruiterChat()}
              placeholder="Query candidates (e.g. 'Who built projects with FastAPI and PostgreSQL?')..."
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button
              onClick={handleRecruiterChat}
              disabled={isChatLoading || !chatInput.trim()}
              className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50 transition-colors flex items-center justify-center shadow-md shadow-emerald-600/25"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* TAB 4: Job Postings & Creator */}
      {activeTab === 'jobs' && (
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-white">Create New Job Posting</h3>
            <p className="text-xs text-slate-400">
              Paste your raw Job Description below. Our AI provider will automatically parse and structure required technical skills, qualifications, and responsibilities.
            </p>

            <form onSubmit={handleCreateJob} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-1">Job Title</label>
                  <input
                    type="text"
                    required
                    value={newJobTitle}
                    onChange={(e) => setNewJobTitle(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer"
                    className="w-full px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-1">Company</label>
                  <input
                    type="text"
                    required
                    value={newJobCompany}
                    onChange={(e) => setNewJobCompany(e.target.value)}
                    placeholder="e.g. Acme Tech"
                    className="w-full px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1">Job Description Text</label>
                <textarea
                  rows={6}
                  required
                  value={newJobDescription}
                  onChange={(e) => setNewJobDescription(e.target.value)}
                  placeholder="Paste complete Job Description with skills, responsibilities, and requirements..."
                  className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs sm:text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isCreatingJob}
                  className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs sm:text-sm font-semibold disabled:opacity-50 shadow-md shadow-emerald-600/25"
                >
                  {isCreatingJob ? 'Extracting & Creating...' : 'Publish Job Posting'}
                </button>
              </div>
            </form>
          </div>

          {selectedJob && (
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Current Active Posting</span>
                  <h4 className="text-lg font-bold text-white mt-0.5">{selectedJob.title}</h4>
                  <span className="text-xs text-slate-400">{selectedJob.company} • {selectedJob.experience_required || '2+ years'}</span>
                </div>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="font-bold text-slate-400 block mb-1">Required Skills:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJob.required_skills?.map((s, i) => (
                      <span key={i} className="px-2.5 py-1 rounded bg-slate-800 text-emerald-300 border border-slate-700 font-medium">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="font-bold text-slate-400 block mb-1">Responsibilities:</span>
                  <ul className="list-disc list-inside text-slate-300 space-y-1">
                    {selectedJob.responsibilities?.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}

        </div>
      )}

      {/* TAB 5: Interview Calendar Slots */}
      {activeTab === 'slots' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
            <div>
              <h3 className="text-base font-bold text-white">Manage Interview Slots</h3>
              <p className="text-xs text-slate-400 mt-1">
                Publish available time slots for shortlisted candidates to self-schedule their interviews.
              </p>
            </div>

            <form onSubmit={handleCreateSlot} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col sm:flex-row gap-4 items-end">
              <div className="flex-1">
                <label className="text-xs font-semibold text-slate-400 block mb-1">Start Time</label>
                <input
                  type="datetime-local"
                  required
                  value={newSlotStart}
                  onChange={(e) => setNewSlotStart(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="flex-1">
                <label className="text-xs font-semibold text-slate-400 block mb-1">End Time</label>
                <input
                  type="datetime-local"
                  required
                  value={newSlotEnd}
                  onChange={(e) => setNewSlotEnd(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>
              <button
                type="submit"
                disabled={!selectedJobId}
                className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/25"
              >
                Add Slot
              </button>
            </form>

            <div className="space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Published Slots</h4>
              {slots.length === 0 ? (
                <p className="text-xs text-slate-500">No interview slots created for this job.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {slots.map(slot => (
                    <div key={slot.id} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                      <div>
                        <span className="text-xs font-semibold text-white block">
                          {new Date(slot.start_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          {new Date(slot.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {new Date(slot.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        slot.status === 'booked' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {slot.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {/* TAB 6: Export Center */}
      {activeTab === 'exports' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl space-y-6">
            <div>
              <h3 className="text-base font-bold text-white">Recruitment Report Exports</h3>
              <p className="text-xs text-slate-400 mt-1">
                Generate high-fidelity reports containing complete candidate rankings, ATS metrics, and evidence-based justifications.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              
              <div className="p-5 rounded-2xl bg-slate-950 border border-indigo-500/30 flex flex-col justify-between space-y-4">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mb-3">
                    <FileText className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-bold text-white">Executive PDF Report</h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Formatted document with summary tables, candidate scores, and evidence analysis.
                  </p>
                </div>
                <a
                  href={selectedJobId ? api.getExportUrl(selectedJobId, 'pdf') : '#'}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full text-center py-2 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors block shadow-md shadow-indigo-600/25"
                >
                  Download PDF Report
                </a>
              </div>

              <div className="p-5 rounded-2xl bg-slate-950 border border-emerald-500/30 flex flex-col justify-between space-y-4">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center mb-3">
                    <ArrowUpDown className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-bold text-white">CSV Spreadsheet</h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Structured CSV file ready for import into ATS systems, Excel, or Google Sheets.
                  </p>
                </div>
                <a
                  href={selectedJobId ? api.getExportUrl(selectedJobId, 'csv') : '#'}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full text-center py-2 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors block shadow-md shadow-emerald-600/25"
                >
                  Download CSV File
                </a>
              </div>

              <div className="p-5 rounded-2xl bg-slate-950 border border-amber-500/30 flex flex-col justify-between space-y-4">
                <div>
                  <div className="w-10 h-10 rounded-xl bg-amber-600/20 text-amber-400 flex items-center justify-center mb-3">
                    <Download className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-bold text-white">JSON Raw Dataset</h4>
                  <p className="text-xs text-slate-400 mt-1">
                    Complete schema payload with nested candidate profiles, skills, and scoring metadata.
                  </p>
                </div>
                <a
                  href={selectedJobId ? api.getExportUrl(selectedJobId, 'json') : '#'}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full text-center py-2 px-4 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold transition-colors block shadow-md shadow-amber-600/25"
                >
                  Download JSON Payload
                </a>
              </div>

            </div>
          </div>
        </div>
      )}

    </div>
  );
};
