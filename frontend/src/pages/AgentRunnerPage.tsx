import React, { useState } from 'react';
import {
  Box, Grid, Typography, TextField, Button, Card, CardContent, FormControl,
  InputLabel, Select, MenuItem, CircularProgress, Alert, Tabs, Tab, Paper,
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';
import { agentApi } from '../services/api';
import { AgentSession, AgentType } from '../types';
import StatusChip from '../components/common/StatusChip';
import AgentTypeChip from '../components/common/AgentTypeChip';
import MermaidDiagram from '../components/common/MermaidDiagram';
import StepTimeline from '../components/common/StepTimeline';

export default function AgentRunnerPage() {
  const [agentType, setAgentType] = useState<AgentType>('react');
  const [message, setMessage] = useState('Please write an email to John requesting confirmation regarding the latest candidate hires.');
  const [userName, setUserName] = useState('John');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentSession | null>(null);
  const [error, setError] = useState('');
  const [tab, setTab] = useState(0);

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await agentApi.runAgent({
        agent_type: agentType,
        message,
        user_name: userName,
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Agent execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Run Agent</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Execute individual agents with custom parameters
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Agent Type</InputLabel>
                <Select value={agentType} label="Agent Type" onChange={e => setAgentType(e.target.value as AgentType)}>
                  <MenuItem value="react">Adaptive ReAct</MenuItem>
                  <MenuItem value="rigid">Rigid Plan-and-Execute</MenuItem>
                  <MenuItem value="multi">Multi-Agent Orchestrator</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label="Message / Task"
                multiline
                rows={4}
                value={message}
                onChange={e => setMessage(e.target.value)}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Target Contact Name"
                value={userName}
                onChange={e => setUserName(e.target.value)}
                helperText="Name to look up in contacts database"
                sx={{ mb: 3 }}
              />

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrow />}
                onClick={handleRun}
                disabled={loading || !message}
              >
                {loading ? 'Running...' : 'Execute Agent'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {result && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                  <AgentTypeChip type={result.agent_type} />
                  <StatusChip status={result.status} />
                  {result.execution_time_ms && (
                    <Typography variant="body2" color="text.secondary">
                      {result.execution_time_ms}ms
                    </Typography>
                  )}
                  {result.retry_count > 0 && (
                    <Typography variant="body2" color="warning.main">
                      {result.retry_count} retries
                    </Typography>
                  )}
                </Box>

                <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
                  <Tab label="Result" />
                  <Tab label="Steps" />
                  <Tab label="Graph" />
                  <Tab label="Raw JSON" />
                </Tabs>

                {tab === 0 && (
                  <Paper sx={{ p: 2, backgroundColor: 'rgba(0,0,0,0.2)' }}>
                    {result.final_result ? (
                      <Box>
                        {(result.final_result as any)?.email_content && (
                          <Box>
                            <Typography variant="subtitle2" color="primary" gutterBottom>Email Generated:</Typography>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {(result.final_result as any).email_content}
                            </Typography>
                          </Box>
                        )}
                        {(result.final_result as any)?.final_answer && (
                          <Box>
                            <Typography variant="subtitle2" color="primary" gutterBottom>Final Answer:</Typography>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {(result.final_result as any).final_answer}
                            </Typography>
                          </Box>
                        )}
                        {(result.final_result as any)?.error && (
                          <Alert severity="error">{(result.final_result as any).error}</Alert>
                        )}
                      </Box>
                    ) : (
                      <Typography color="text.secondary">No result data</Typography>
                    )}
                  </Paper>
                )}

                {tab === 1 && <StepTimeline steps={result.steps || []} />}

                {tab === 2 && result.graph_definition?.mermaid && (
                  <MermaidDiagram chart={result.graph_definition.mermaid} />
                )}

                {tab === 3 && (
                  <Box sx={{
                    fontFamily: 'monospace', fontSize: '0.8rem',
                    maxHeight: 400, overflow: 'auto', p: 2,
                    backgroundColor: '#0a0a15', borderRadius: 1,
                  }}>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
