// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://172.25.82.250:8000';

export const API_ENDPOINTS = {
  // Authentication
  login: `${API_BASE_URL}/api/auth/login`,
  logout: `${API_BASE_URL}/api/auth/logout`,
  
  // Documents
  uploadDocument: `${API_BASE_URL}/api/documents/upload`,
  getDocument: (id: string) => `${API_BASE_URL}/api/documents/${id}`,
  listDocuments: `${API_BASE_URL}/api/documents`,
  
  // Workflows
  createWorkflow: `${API_BASE_URL}/api/workflows/create`,
  getWorkflow: (id: string) => `${API_BASE_URL}/api/workflows/${id}`,
  listWorkflows: `${API_BASE_URL}/api/workflows`,
  
  // Stages
  processStage: (stage: number) => `${API_BASE_URL}/api/stages/${stage}/process`,
  confirmStage: (stage: number) => `${API_BASE_URL}/api/stages/${stage}/confirm`,
  getStageData: (documentId: string, stage: number) => `${API_BASE_URL}/api/stages/${documentId}/${stage}`,
  
  // Reports
  generateReport: `${API_BASE_URL}/api/reports/generate`,
  getReport: (id: string) => `${API_BASE_URL}/api/reports/${id}`,
  downloadReport: (id: string) => `${API_BASE_URL}/api/reports/${id}/download`,
  
  // Analytics
  getAnalytics: `${API_BASE_URL}/api/analytics`,
  getMetrics: `${API_BASE_URL}/api/analytics/metrics`,
};