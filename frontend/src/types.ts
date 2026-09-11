export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'candidate' | 'recruiter' | 'admin';
  created_at: string;
}

export interface ExperienceItem {
  company: string;
  role: string;
  duration?: string;
  description?: string;
}

export interface EducationItem {
  degree: string;
  university?: string;
  cgpa?: number;
  year?: string;
}

export interface ProjectItem {
  name: string;
  description?: string;
  technologies: string[];
  link?: string;
  impact?: string;
}

export interface ParsedProfile {
  name?: string;
  contact_info: {
    email?: string;
    phone?: string;
    linkedin?: string;
    github?: string;
    portfolio?: string;
  };
  skills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: ProjectItem[];
  certifications: string[];
  achievements: string[];
  total_experience_years: number;
}

export interface ATSAnalysis {
  ats_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  best_project_analysis?: string;
}

export interface ResumeData {
  id: string;
  candidate_id: string;
  file_name?: string;
  file_url?: string;
  uploaded_at: string;
  profile?: ParsedProfile;
  ats_analysis?: ATSAnalysis;
}

export interface Job {
  id: string;
  recruiter_id: string;
  title: string;
  company: string;
  description: string;
  required_skills: string[];
  nice_to_have_skills: string[];
  qualifications: string[];
  responsibilities: string[];
  experience_required?: string;
  created_at: string;
}

export interface MatchResult {
  id: string;
  job_id: string;
  candidate_id: string;
  resume_id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  classification: 'shortlist' | 'maybe' | 'reject';
  ranking_explanation?: string;
  evidence_quotes: string[];
  created_at: string;
}

export interface RankedCandidate {
  rank: number;
  match_id: string;
  candidate_id: string;
  candidate_name: string;
  candidate_email?: string;
  resume_id: string;
  match_score: number;
  classification: 'shortlist' | 'maybe' | 'reject';
  matched_skills: string[];
  missing_skills: string[];
  total_experience_years: number;
  ranking_explanation: string;
  evidence_quotes: string[];
}

export interface QuestionSet {
  technical: string[];
  project: string[];
  behavioral: string[];
  follow_up: string[];
}

export interface MockInterviewStep {
  question: string;
  answer: string;
  feedback: string;
  score: number;
  strengths?: string[];
  improvements?: string[];
}

export interface MockInterviewSession {
  id: string;
  candidate_id: string;
  job_id?: string;
  questions: string[];
  transcript: MockInterviewStep[];
  scores: {
    technical?: number;
    communication?: number;
    projects?: number;
    problem_solving?: number;
  };
  readiness_score: number;
  feedback?: string;
  status: 'in_progress' | 'completed';
  created_at: string;
}

export interface InterviewSlot {
  id: string;
  recruiter_id: string;
  job_id: string;
  candidate_id?: string;
  start_time: string;
  end_time: string;
  status: 'available' | 'booked' | 'cancelled';
  booked_at?: string;
}

export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}
