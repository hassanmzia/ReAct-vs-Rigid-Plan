import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, CircularProgress, Card, CardContent, Tabs, Tab } from '@mui/material';
import { graphApi } from '../services/api';
import MermaidDiagram from '../components/common/MermaidDiagram';

const AGENT_LABELS: Record<string, string> = {
  react: 'Adaptive ReAct Agent',
  rigid: 'Rigid Plan-and-Execute Agent',
  multi: 'Multi-Agent Orchestrator',
  recursive: 'Recursive Q&A Tuneup',
};

const AGENT_DESCRIPTIONS: Record<string, string> = {
  react: 'Uses conditional routing and LLM-based disambiguation to handle ambiguous contact lookups. Implements retry logic with adaptive reasoning loops.',
  rigid: 'Follows a fixed sequential plan: Plan -> Contact Lookup -> Email Send. Fails on ambiguous results without retry capability.',
  multi: 'Coordinates Research, Reasoning, and Action agents through a Supervisor. Implements A2A (Agent-to-Agent) communication patterns.',
  recursive: 'Iteratively refines queries and evaluates answer quality. Continues until confidence threshold is met or max iterations reached.',
};

export default function GraphsPage() {
  const [graphs, setGraphs] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState(0);
  const agentTypes = ['react', 'rigid', 'multi', 'recursive'];

  useEffect(() => {
    graphApi.getAllGraphs()
      .then(res => setGraphs(res.data || {}))
      .catch(() => setGraphs({}))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Agent Graphs</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        LangGraph workflow visualizations using Mermaid diagrams
      </Typography>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        {agentTypes.map(type => (
          <Tab key={type} label={AGENT_LABELS[type]} />
        ))}
      </Tabs>

      {agentTypes.map((type, idx) => (
        tab === idx && (
          <Box key={type}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>{AGENT_LABELS[type]}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {AGENT_DESCRIPTIONS[type]}
                </Typography>
              </CardContent>
            </Card>
            {graphs[type] ? (
              <MermaidDiagram chart={graphs[type]} title="Workflow Graph" />
            ) : (
              <Typography color="text.secondary">Graph not available</Typography>
            )}
          </Box>
        )
      ))}
    </Box>
  );
}
