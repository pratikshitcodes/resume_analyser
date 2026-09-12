import axios from 'axios';

// Resolve Backend API URL dynamically
const getBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) {
    const clean = envUrl.replace(/\/+$/, '');
    return clean.endsWith('/api/v1') ? clean : `${clean}/api/v1`;
  }
  // In development fallback to localhost, in production fallback to deployed Render backend
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://talentplus-ai.onrender.com/api/v1';
  }
  return 'http://127.0.0.1:8000/api/v1';
};

const API_BASE_URL = getBaseUrl();

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

// Response interceptor for automatic token refresh on 401
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/login') && !originalRequest.url?.includes('/auth/register') && !originalRequest.url?.includes('/auth/refresh')) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken });
          const { access_token, refresh_token: newRefreshToken } = res.data;
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          processQueue(null, access_token);
          return apiClient(originalRequest);
        } catch (refreshErr) {
          processQueue(refreshErr, null);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('app_role');
          window.dispatchEvent(new Event('auth:logout'));
          return Promise.reject(refreshErr);
        } finally {
          isRefreshing = false;
        }
      }
    }
    return Promise.reject(error);
  }
);

// API Functions
export const api = {
  // Auth
  register: (data: any) => apiClient.post('/auth/register', data),
  login: (data: any) => apiClient.post('/auth/login', data),
  refreshToken: (refreshToken: string) => axios.post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken }),
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
