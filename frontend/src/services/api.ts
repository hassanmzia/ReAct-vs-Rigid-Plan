import axios from 'axios';
import {
  AgentSession,
  AgentComparison,
  Contact,
  Document,
  DashboardStats,
  RunAgentRequest,
  CompareRequest,
  RecursiveQARequest,
} from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://172.168.1.95:8042';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Agents ───────────────────────────────────────────

export const agentApi = {
  runAgent: (data: RunAgentRequest) =>
    api.post<AgentSession>('/agents/sessions/run-sync/', data),

  runAgentAsync: (data: RunAgentRequest) =>
    api.post('/agents/sessions/run/', data),

  compareAgents: (data: CompareRequest) =>
    api.post<AgentComparison>('/agents/sessions/compare-sync/', data),

  recursiveQA: (data: RecursiveQARequest) =>
    api.post<AgentSession>('/agents/sessions/recursive-qa-sync/', data),

  getSessions: (params?: Record<string, string>) =>
    api.get<{ results: AgentSession[] }>('/agents/sessions/', { params }),

  getSession: (id: string) =>
    api.get<AgentSession>(`/agents/sessions/${id}/`),

  getComparisons: () =>
    api.get<{ results: AgentComparison[] }>('/agents/comparisons/'),

  getComparison: (id: string) =>
    api.get<AgentComparison>(`/agents/comparisons/${id}/`),
};

// ─── Graphs ───────────────────────────────────────────

export const graphApi = {
  getMermaid: (agentType: string) =>
    api.get('/agents/graph/', { params: { agent_type: agentType, format: 'mermaid' } }),

  getGraphJson: (agentType: string) =>
    api.get('/agents/graph/', { params: { agent_type: agentType, format: 'json' } }),

  getAllGraphs: () =>
    api.get('/agents/graphs/', { params: { format: 'mermaid' } }),
};

// ─── Contacts ─────────────────────────────────────────

export const contactApi = {
  getAll: () => api.get<{ results: Contact[] }>('/agents/contacts/'),
  get: (id: number) => api.get<Contact>(`/agents/contacts/${id}/`),
  create: (data: Partial<Contact>) => api.post<Contact>('/agents/contacts/', data),
  update: (id: number, data: Partial<Contact>) => api.put<Contact>(`/agents/contacts/${id}/`, data),
  delete: (id: number) => api.delete(`/agents/contacts/${id}/`),
};

// ─── Documents ────────────────────────────────────────

export const documentApi = {
  getAll: () => api.get<{ results: Document[] }>('/documents/'),
  get: (id: string) => api.get<Document>(`/documents/${id}/`),
  upload: (file: File, title?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    return api.post<Document>('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: string) => api.delete(`/documents/${id}/`),
  search: (query: string) =>
    api.get('/documents/search/', { params: { q: query } }),
  getChunks: (id: string) => api.get(`/documents/${id}/chunks/`),
};

// ─── Analytics ────────────────────────────────────────

export const analyticsApi = {
  getDashboard: () => api.get<DashboardStats>('/analytics/dashboard/'),
  getTrends: (days?: number) =>
    api.get('/analytics/trends/', { params: { days: days || 7 } }),
  getLeaderboard: () => api.get('/analytics/leaderboard/'),
};

// ─── Health ───────────────────────────────────────────

export const healthApi = {
  check: () => api.get('/health/'),
};

export default api;
