import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Grid, CircularProgress, Alert, Tabs, Tab,
} from '@mui/material';
import { agentApi } from '../services/api';
import { AgentSession } from '../types';
import StatusChip from '../components/common/StatusChip';
import AgentTypeChip from '../components/common/AgentTypeChip';
import MermaidDiagram from '../components/common/MermaidDiagram';
import StepTimeline from '../components/common/StepTimeline';

export default function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<AgentSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState(0);

  useEffect(() => {
    if (!id) return;
    agentApi.getSession(id)
      .then(res => setSession(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  if (error || !session) {
    return <Alert severity="error">{error || 'Session not found'}</Alert>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Session Detail</Typography>
        <AgentTypeChip type={session.agent_type} />
        <StatusChip status={session.status} />
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Execution Time</Typography>
              <Typography variant="h5">{session.execution_time_ms || '-'} ms</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Retries</Typography>
              <Typography variant="h5">{session.retry_count}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">Created</Typography>
              <Typography variant="h6">{new Date(session.created_at).toLocaleString()}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary">Query</Typography>
          <Typography variant="body1">{session.user_message}</Typography>
          {session.user_name_target && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Target: {session.user_name_target}
            </Typography>
          )}
        </CardContent>
      </Card>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Result" />
        <Tab label="Steps" />
        <Tab label="Graph" />
        <Tab label="Q&A History" />
        <Tab label="Raw JSON" />
      </Tabs>

      {tab === 0 && session.final_result && (
        <Card>
          <CardContent>
            <Box sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.85rem' }}>
              {JSON.stringify(session.final_result, null, 2)}
            </Box>
          </CardContent>
        </Card>
      )}

      {tab === 1 && <StepTimeline steps={session.steps || []} title="Execution Steps" />}

      {tab === 2 && session.graph_definition?.mermaid && (
        <MermaidDiagram chart={session.graph_definition.mermaid} title="Agent Workflow Graph" />
      )}

      {tab === 3 && (
        <Card>
          <CardContent>
            {session.query_history?.length > 0 ? (
              session.query_history.map((qh, i) => (
                <Box key={qh.id} sx={{ mb: 2, p: 2, backgroundColor: 'rgba(0,0,0,0.2)', borderRadius: 1 }}>
                  <Typography variant="subtitle2">Iteration {qh.iteration}</Typography>
                  <Typography variant="body2" color="text.secondary">Query: {qh.refined_query || qh.original_query}</Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>{qh.answer}</Typography>
                  {qh.confidence_score !== null && (
                    <Typography variant="caption" color="primary">
                      Confidence: {(qh.confidence_score * 100).toFixed(1)}%
                    </Typography>
                  )}
                </Box>
              ))
            ) : (
              <Typography color="text.secondary">No Q&A history for this session</Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tab === 4 && (
        <Box sx={{
          fontFamily: 'monospace', fontSize: '0.8rem',
          maxHeight: 500, overflow: 'auto', p: 2,
          backgroundColor: '#0a0a15', borderRadius: 1,
        }}>
          <pre>{JSON.stringify(session, null, 2)}</pre>
        </Box>
      )}
    </Box>
  );
}
