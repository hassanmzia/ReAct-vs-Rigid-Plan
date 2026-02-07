import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, CircularProgress, IconButton, Tooltip, FormControl,
  InputLabel, Select, MenuItem,
} from '@mui/material';
import { Visibility } from '@mui/icons-material';
import { agentApi } from '../services/api';
import { AgentSession } from '../types';
import StatusChip from '../components/common/StatusChip';
import AgentTypeChip from '../components/common/AgentTypeChip';

export default function SessionsPage() {
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const params: Record<string, string> = {};
    if (filter) params.agent_type = filter;
    agentApi.getSessions(params)
      .then(res => setSessions(res.data?.results || []))
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, [filter]);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4">Sessions</Typography>
          <Typography variant="body1" color="text.secondary">Agent execution history</Typography>
        </Box>
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Filter by Type</InputLabel>
          <Select value={filter} label="Filter by Type" onChange={e => setFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="react">ReAct</MenuItem>
            <MenuItem value="rigid">Rigid</MenuItem>
            <MenuItem value="multi">Multi-Agent</MenuItem>
            <MenuItem value="recursive">Recursive Q&A</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Message</TableCell>
                <TableCell align="right">Time (ms)</TableCell>
                <TableCell align="right">Retries</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sessions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No sessions found. Run an agent to get started.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sessions.map(session => (
                  <TableRow key={session.id} hover>
                    <TableCell><AgentTypeChip type={session.agent_type} /></TableCell>
                    <TableCell><StatusChip status={session.status} /></TableCell>
                    <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {session.user_message}
                    </TableCell>
                    <TableCell align="right">{session.execution_time_ms || '-'}</TableCell>
                    <TableCell align="right">{session.retry_count}</TableCell>
                    <TableCell>{new Date(session.created_at).toLocaleString()}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => navigate(`/sessions/${session.id}`)}>
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
}
