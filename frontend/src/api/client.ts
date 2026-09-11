import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Attach JWT token automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API Functions
export const api = {
  // Auth
  register: (data: any) => apiClient.post('/auth/register', data),
  login: (data: any) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),

  // Candidate
  uploadResume: (formData: FormData) => apiClient.post('/candidate/upload-resume', formData),
  getLatestResume: () => apiClient.get('/candidate/resume/latest'),
  candidateChat: (data: { message: string; session_id?: string }) => apiClient.post('/candidate/chat', data),
  evaluateJDFit: (formData: FormData) => apiClient.post('/candidate/evaluate-jd', formData),
  getInterviewQuestions: (jobId?: string) => apiClient.get('/candidate/questions', { params: { job_id: jobId } }),
  startMockInterview: (data: { job_id?: string; num_questions?: number }) => apiClient.post('/candidate/mock-interview/start', data),
  stepMockInterview: (data: { session_id: string; question_index: number; user_answer: string }) => apiClient.post('/candidate/mock-interview/step', data),
  getMockInterviewSession: (sessionId: string) => apiClient.get(`/candidate/mock-interview/${sessionId}`),
  getAvailableSlots: (jobId?: string) => apiClient.get('/candidate/available-slots', { params: { job_id: jobId } }),
  bookSlot: (slotId: string) => apiClient.post(`/candidate/book-slot/${slotId}`),

  // Recruiter
  createJob: (data: { title: string; company?: string; description: string; experience_required?: string }) => apiClient.post('/recruiter/jobs', data),
  getJobs: () => apiClient.get('/recruiter/jobs'),
  getJob: (jobId: string) => apiClient.get(`/recruiter/jobs/${jobId}`),
  batchUploadResumes: (jobId: string, formData: FormData) => apiClient.post(`/recruiter/jobs/${jobId}/batch-upload`, formData),
  getRankings: (jobId: string, classification?: string) => apiClient.get(`/recruiter/jobs/${jobId}/rankings`, { params: { classification } }),
  recruiterChat: (jobId: string, data: { message: string; session_id?: string }) => apiClient.post(`/recruiter/jobs/${jobId}/chat`, data),
  createInterviewSlot: (jobId: string, data: { job_id: string; start_time: string; end_time: string }) => apiClient.post(`/recruiter/jobs/${jobId}/slots`, data),
  getInterviewSlots: (jobId: string) => apiClient.get(`/recruiter/jobs/${jobId}/slots`),

  // Exports
  getExportUrl: (jobId: string, format: 'csv' | 'json' | 'pdf') => `${API_BASE_URL}/recruiter/jobs/${jobId}/export/${format}`,

  // Background Tasks
  getTaskStatus: (taskId: string) => apiClient.get(`/tasks/${taskId}`),
};
