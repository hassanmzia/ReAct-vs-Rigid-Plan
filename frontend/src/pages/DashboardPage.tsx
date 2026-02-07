import React, { useEffect, useState } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, CircularProgress, Paper,
} from '@mui/material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { analyticsApi } from '../services/api';
import { DashboardStats } from '../types';

const COLORS = ['#6C63FF', '#FF6584', '#4CAF50', '#FF9800', '#2196F3'];

function StatCard({ title, value, subtitle, color }: {
  title: string; value: string | number; subtitle?: string; color: string;
}) {
  return (
    <Card sx={{ borderLeft: `4px solid ${color}` }}>
      <CardContent>
        <Typography variant="body2" color="text.secondary">{title}</Typography>
        <Typography variant="h4" sx={{ fontWeight: 700, color }}>{value}</Typography>
        {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsApi.getDashboard().catch(() => ({ data: null })),
      analyticsApi.getTrends(7).catch(() => ({ data: { trends: [] } })),
      analyticsApi.getLeaderboard().catch(() => ({ data: [] })),
    ]).then(([dashRes, trendRes, lbRes]) => {
      setStats(dashRes.data);
      setTrends(trendRes.data?.trends || []);
      setLeaderboard(Array.isArray(lbRes.data) ? lbRes.data : []);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  const overview = stats?.overview;
  const compData = stats?.comparisons;

  const pieData = compData ? [
    { name: 'ReAct Wins', value: compData.react_wins },
    { name: 'Rigid Wins', value: compData.rigid_wins },
    { name: 'Tie / None', value: compData.tie_or_none },
  ] : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        AI Recursive Q&A Tuneup System - Performance Overview
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Sessions" value={overview?.total_sessions || 0} subtitle="All time" color="#6C63FF" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Last 24h" value={overview?.recent_sessions_24h || 0} subtitle="Recent activity" color="#2196F3" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Success Rate" value={`${overview?.success_rate || 0}%`} subtitle="Completed sessions" color="#4CAF50" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Documents" value={overview?.total_documents || 0} subtitle={`${overview?.processed_documents || 0} processed`} color="#FF9800" />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>7-Day Activity Trends</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends}>
                <XAxis dataKey="date" tick={{ fill: '#aaa', fontSize: 12 }} />
                <YAxis tick={{ fill: '#aaa' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1A1A2E', border: '1px solid #333' }} />
                <Legend />
                <Bar dataKey="completed" fill="#4CAF50" name="Completed" />
                <Bar dataKey="failed" fill="#f44336" name="Failed" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Agent Comparison Results</Typography>
            {pieData.some(d => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value" label>
                    {pieData.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#1A1A2E', border: '1px solid #333' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 8 }}>
                No comparison data yet. Run a comparison to see results.
              </Typography>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Agent Leaderboard</Typography>
            <Grid container spacing={2}>
              {leaderboard.map((agent, i) => (
                <Grid item xs={12} sm={6} md={3} key={agent.agent_type}>
                  <Card sx={{
                    border: i === 0 ? '2px solid #FFD700' : '1px solid rgba(255,255,255,0.08)',
                    position: 'relative',
                  }}>
                    {i === 0 && (
                      <Box sx={{
                        position: 'absolute', top: -10, right: 10,
                        backgroundColor: '#FFD700', color: '#000',
                        px: 1, borderRadius: 1, fontSize: '0.75rem', fontWeight: 700,
                      }}>
                        TOP
                      </Box>
                    )}
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        {agent.agent_type.toUpperCase()}
                      </Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, color: COLORS[i] }}>
                        {agent.success_rate}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {agent.total_runs} runs | Avg {Math.round(agent.avg_execution_ms || 0)}ms
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
