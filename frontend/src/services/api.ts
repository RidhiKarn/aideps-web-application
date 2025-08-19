import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://172.25.82.250:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    }
    return Promise.reject(error);
  }
);

// Document APIs
export const documentAPI = {
  upload: async (file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });
    
    return api.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / (progressEvent.total || 1)
        );
        // You can use this to update a progress bar
        console.log('Upload progress:', percentCompleted);
      },
    });
  },
  
  get: (documentId: string) => api.get(`/api/documents/${documentId}`),
  
  preview: (documentId: string, rows: number = 10) =>
    api.get(`/api/documents/${documentId}/preview`, { params: { rows } }),
  
  updateSchema: (documentId: string, schema: any) =>
    api.post(`/api/documents/${documentId}/schema`, schema),
};

// Workflow APIs
export const workflowAPI = {
  get: (workflowId: string) => api.get(`/api/workflows/${workflowId}`),
  
  getStatus: (workflowId: string) => api.get(`/api/workflows/${workflowId}/status`),
  
  startStage: (workflowId: string, stageNumber: number) =>
    api.post(`/api/workflows/${workflowId}/stages/${stageNumber}/start`),
  
  completeStage: (workflowId: string, stageNumber: number, data?: any) =>
    api.post(`/api/workflows/${workflowId}/stages/${stageNumber}/complete`, data),
  
  reviewStage: (workflowId: string, stageNumber: number, reviewData: any) =>
    api.post(`/api/workflows/${workflowId}/stages/${stageNumber}/review`, reviewData),
  
  navigateToStage: (workflowId: string, stageNumber: number) =>
    api.post(`/api/workflows/${workflowId}/navigate/${stageNumber}`),
  
  getHistory: (workflowId: string) => api.get(`/api/workflows/${workflowId}/history`),
};

// Stage-specific APIs
export const stageAPI = {
  // Stage 2: Cleansing
  analyzeQuality: (workflowId: string, documentId: string) =>
    api.post('/api/stages/cleansing/analyze', null, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  imputeMissing: (workflowId: string, documentId: string, config: any) =>
    api.post('/api/stages/cleansing/impute', config, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  handleOutliers: (workflowId: string, documentId: string, config: any) =>
    api.post('/api/stages/cleansing/outliers', config, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  // Stage 3: Analysis
  discoverPatterns: (workflowId: string, documentId: string) =>
    api.post('/api/stages/analysis/discover', null, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  // Stage 4: Statistics
  calculateStatistics: (workflowId: string, documentId: string, config: any) =>
    api.post('/api/stages/statistics/calculate', config, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
};

// Report APIs
export const reportAPI = {
  propose: (workflowId: string, documentId: string, config: any) =>
    api.post('/api/reports/propose', config, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  confirm: (workflowId: string, documentId: string, selection: any) =>
    api.post('/api/reports/confirm', selection, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  generate: (workflowId: string, documentId: string) =>
    api.post('/api/reports/generate', null, {
      params: { workflow_id: workflowId, document_id: documentId },
    }),
  
  download: (documentId: string, reportType: string) =>
    api.get(`/api/reports/download/${documentId}/${reportType}`, {
      responseType: 'blob',
    }),
  
  getTemplates: () => api.get('/api/reports/templates'),
};

export default api;