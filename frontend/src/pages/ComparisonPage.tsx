import React, { useState } from 'react';
import {
  Box, Grid, Typography, TextField, Button, Card, CardContent,
  CircularProgress, Alert, Divider, Chip,
} from '@mui/material';
import { Compare } from '@mui/icons-material';
import { agentApi } from '../services/api';
import { AgentComparison } from '../types';
import StatusChip from '../components/common/StatusChip';
import MermaidDiagram from '../components/common/MermaidDiagram';

export default function ComparisonPage() {
  const [message, setMessage] = useState('Please write an email to John requesting confirmation regarding the latest candidate hires.');
  const [userName, setUserName] = useState('John');
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState<AgentComparison | null>(null);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await agentApi.compareAgents({ message, user_name: userName });
      setComparison(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  const renderSessionCard = (session: any, label: string, color: string) => (
    <Card sx={{ border: `2px solid ${color}`, flex: 1 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ color }}>{label}</Typography>
          <StatusChip status={session.status} />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Execution Time: {session.execution_time_ms || 'N/A'}ms
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Retries: {session.retry_count || 0}
        </Typography>
        <Divider sx={{ my: 2 }} />
        {session.final_result ? (
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            {session.final_result.email_content && (
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {session.final_result.email_content}
              </Typography>
            )}
            {session.final_result.email_result && (
              <Typography variant="body2">{session.final_result.email_result}</Typography>
            )}
            {session.final_result.error && (
              <Alert severity="error" sx={{ mt: 1 }}>{session.final_result.error}</Alert>
            )}
          </Box>
        ) : (
          <Typography color="text.secondary">No result</Typography>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Compare Agents</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Run ReAct vs Rigid agents side-by-side on the same task
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Task Message"
                multiline
                rows={3}
                value={message}
                onChange={e => setMessage(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Target Contact"
                value={userName}
                onChange={e => setUserName(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Compare />}
                onClick={handleCompare}
                disabled={loading || !message}
              >
                {loading ? 'Comparing...' : 'Compare Agents'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {comparison && (
        <Box>
          <Card sx={{ mb: 3, textAlign: 'center', py: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Winner</Typography>
              <Chip
                label={comparison.winner === 'react' ? 'ReAct Agent' :
                       comparison.winner === 'rigid' ? 'Rigid Agent' : 'No Winner'}
                color={comparison.winner === 'none' ? 'default' : 'success'}
                size="medium"
                sx={{ fontSize: '1.1rem', py: 2.5, px: 2 }}
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                {comparison.analysis}
              </Typography>
            </CardContent>
          </Card>

          <Box sx={{ display: 'flex', gap: 3 }}>
            {renderSessionCard(comparison.react_session, 'Adaptive ReAct', '#4CAF50')}
            {renderSessionCard(comparison.rigid_session, 'Rigid Plan-and-Execute', '#FF9800')}
          </Box>
        </Box>
      )}
    </Box>
  );
}
