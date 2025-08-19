import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { Toaster } from 'react-hot-toast';

import { theme } from './theme';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { WorkflowPage } from './pages/WorkflowPage';
import { LoginPage } from './pages/LoginPage';
import { useAuthStore } from './store/authStore';

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              isAuthenticated ? <Layout /> : <Navigate to="/login" />
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="workflow/new" element={<WorkflowPage />} />
            <Route path="workflow/:documentId/:stage" element={<WorkflowPage />} />
            <Route path="workflow/:documentId" element={<WorkflowPage />} />
          </Route>
        </Routes>
      </Router>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#4caf50',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#f44336',
              secondary: '#fff',
            },
          },
        }}
      />
    </ThemeProvider>
  );
}

export default App;