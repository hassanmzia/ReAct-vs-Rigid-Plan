import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { SnackbarProvider } from 'notistack';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import AgentRunnerPage from './pages/AgentRunnerPage';
import ComparisonPage from './pages/ComparisonPage';
import RecursiveQAPage from './pages/RecursiveQAPage';
import SessionsPage from './pages/SessionsPage';
import SessionDetailPage from './pages/SessionDetailPage';
import DocumentsPage from './pages/DocumentsPage';
import GraphsPage from './pages/GraphsPage';
import ContactsPage from './pages/ContactsPage';
import MCPPage from './pages/MCPPage';
import A2APage from './pages/A2APage';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6C63FF' },
    secondary: { main: '#FF6584' },
    background: {
      default: '#0F0F1A',
      paper: '#1A1A2E',
    },
    success: { main: '#4CAF50' },
    warning: { main: '#FF9800' },
    error: { main: '#f44336' },
    info: { main: '#2196F3' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255,255,255,0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600 },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/run" element={<AgentRunnerPage />} />
              <Route path="/compare" element={<ComparisonPage />} />
              <Route path="/recursive-qa" element={<RecursiveQAPage />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:id" element={<SessionDetailPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/graphs" element={<GraphsPage />} />
              <Route path="/contacts" element={<ContactsPage />} />
              <Route path="/mcp" element={<MCPPage />} />
              <Route path="/a2a" element={<A2APage />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;
