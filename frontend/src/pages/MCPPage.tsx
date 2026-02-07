import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Button, TextField,
  Select, MenuItem, FormControl, InputLabel, Alert, Paper,
} from '@mui/material';
import { Hub, PlayArrow } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://172.168.1.95:8042';

const MCP_TOOLS = [
  {
    name: 'contact_lookup',
    description: 'Look up a contact in the corporate database by name',
    parameters: { name: 'string' },
  },
  {
    name: 'run_react_agent',
    description: 'Execute an Adaptive ReAct agent for a given task',
    parameters: { message: 'string', user_name: 'string (optional)' },
  },
  {
    name: 'run_rigid_agent',
    description: 'Execute a Rigid Plan-and-Execute agent for a given task',
    parameters: { message: 'string', user_name: 'string (optional)' },
  },
  {
    name: 'recursive_qa',
    description: 'Run recursive Q&A with iterative refinement',
    parameters: { query: 'string', max_refinements: 'int', target_confidence: 'float' },
  },
  {
    name: 'compare_agents',
    description: 'Compare ReAct vs Rigid agent execution on the same task',
    parameters: { message: 'string', user_name: 'string (optional)' },
  },
];

export default function MCPPage() {
  const [selectedTool, setSelectedTool] = useState('contact_lookup');
  const [inputJson, setInputJson] = useState('{"name": "John"}');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInvoke = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const args = JSON.parse(inputJson);
      let res;

      if (selectedTool === 'contact_lookup') {
        res = await axios.get(`${API_URL}/api/agents/contacts/`, { params: { search: args.name } });
      } else if (selectedTool === 'run_react_agent') {
        res = await axios.post(`${API_URL}/api/agents/sessions/run-sync/`, {
          agent_type: 'react', message: args.message, user_name: args.user_name || '',
        });
      } else if (selectedTool === 'run_rigid_agent') {
        res = await axios.post(`${API_URL}/api/agents/sessions/run-sync/`, {
          agent_type: 'rigid', message: args.message, user_name: args.user_name || '',
        });
      } else if (selectedTool === 'recursive_qa') {
        res = await axios.post(`${API_URL}/api/agents/sessions/recursive-qa-sync/`, args);
      } else if (selectedTool === 'compare_agents') {
        res = await axios.post(`${API_URL}/api/agents/sessions/compare-sync/`, args);
      }

      setResult(res?.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Invocation failed');
    } finally {
      setLoading(false);
    }
  };

  const selectedToolInfo = MCP_TOOLS.find(t => t.name === selectedTool);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>MCP Tools</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Model Context Protocol - Expose agent capabilities as tools for external AI systems
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Available Tools</Typography>
              {MCP_TOOLS.map(tool => (
                <Paper
                  key={tool.name}
                  onClick={() => setSelectedTool(tool.name)}
                  sx={{
                    p: 2, mb: 1, cursor: 'pointer',
                    border: selectedTool === tool.name ? '2px solid #6C63FF' : '1px solid rgba(255,255,255,0.08)',
                    '&:hover': { borderColor: '#6C63FF' },
                  }}
                >
                  <Typography variant="subtitle2" color="primary">{tool.name}</Typography>
                  <Typography variant="caption" color="text.secondary">{tool.description}</Typography>
                  <Box sx={{ mt: 1 }}>
                    {Object.entries(tool.parameters).map(([k, v]) => (
                      <Chip key={k} label={`${k}: ${v}`} size="small" sx={{ mr: 0.5, mb: 0.5 }} variant="outlined" />
                    ))}
                  </Box>
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Tool: {selectedToolInfo?.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {selectedToolInfo?.description}
              </Typography>

              <TextField
                fullWidth
                label="Input JSON"
                multiline
                rows={4}
                value={inputJson}
                onChange={e => setInputJson(e.target.value)}
                sx={{ mb: 2, fontFamily: 'monospace' }}
              />

              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={handleInvoke}
                disabled={loading}
              >
                {loading ? 'Invoking...' : 'Invoke Tool'}
              </Button>
            </CardContent>
          </Card>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {result && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Result</Typography>
                <Box sx={{
                  fontFamily: 'monospace', fontSize: '0.85rem',
                  maxHeight: 400, overflow: 'auto', p: 2,
                  backgroundColor: '#0a0a15', borderRadius: 1,
                }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(result, null, 2)}
                  </pre>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
