import React from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Paper, Avatar,
} from '@mui/material';
import { SmartToy, Psychology, Description, AccountTree, Compare } from '@mui/icons-material';

const A2A_AGENTS = [
  {
    id: 'react-agent',
    name: 'Adaptive ReAct Agent',
    description: 'Handles ambiguous tasks using LLM-based reasoning loops. Implements conditional routing with retry logic for contact disambiguation.',
    capabilities: ['contact_lookup', 'email_send', 'disambiguation'],
    icon: <Psychology />,
    color: '#4CAF50',
  },
  {
    id: 'rigid-agent',
    name: 'Rigid Plan-and-Execute Agent',
    description: 'Executes fixed workflow plans sequentially. Simple and predictable but fails on ambiguous scenarios.',
    capabilities: ['contact_lookup', 'email_send'],
    icon: <AccountTree />,
    color: '#FF9800',
  },
  {
    id: 'multi-agent',
    name: 'Multi-Agent Orchestrator',
    description: 'Coordinates Research, Reasoning, and Action agents via a Supervisor. Implements full A2A message passing.',
    capabilities: ['research', 'reasoning', 'action', 'synthesis'],
    icon: <SmartToy />,
    color: '#9C27B0',
  },
  {
    id: 'recursive-qa',
    name: 'Recursive Q&A Agent',
    description: 'Iteratively refines queries for high-confidence answers. Tracks confidence scores and refinement history.',
    capabilities: ['qa', 'refinement', 'confidence_scoring'],
    icon: <Compare />,
    color: '#2196F3',
  },
  {
    id: 'document-agent',
    name: 'Document Processing Agent',
    description: 'Processes and indexes PDF documents for RAG. Handles text extraction, chunking, and embedding.',
    capabilities: ['pdf_processing', 'text_extraction', 'indexing'],
    icon: <Description />,
    color: '#E91E63',
  },
];

export default function A2APage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>A2A Agents</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Agent-to-Agent Protocol - Discover and interact with registered agents
      </Typography>

      <Card sx={{ mb: 3, p: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>A2A Protocol Overview</Typography>
          <Typography variant="body2" color="text.secondary">
            The Agent-to-Agent (A2A) protocol enables inter-agent communication through:
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {[
              { label: 'Agent Cards', desc: 'Self-describing capability advertisements' },
              { label: 'Task Delegation', desc: 'Route tasks to the most capable agent' },
              { label: 'Message Passing', desc: 'Structured communication between agents' },
              { label: 'Capability Discovery', desc: 'Find agents by their capabilities' },
            ].map(item => (
              <Grid item xs={12} sm={6} md={3} key={item.label}>
                <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                  <Typography variant="subtitle2" color="primary">{item.label}</Typography>
                  <Typography variant="caption" color="text.secondary">{item.desc}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {A2A_AGENTS.map(agent => (
          <Grid item xs={12} md={6} key={agent.id}>
            <Card sx={{ height: '100%', borderLeft: `4px solid ${agent.color}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar sx={{ backgroundColor: `${agent.color}22`, color: agent.color }}>
                    {agent.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6">{agent.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {agent.id} | Protocol: a2a/1.0
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {agent.description}
                </Typography>
                <Box>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Capabilities:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                    {agent.capabilities.map(cap => (
                      <Chip
                        key={cap}
                        label={cap}
                        size="small"
                        sx={{ backgroundColor: `${agent.color}22`, color: agent.color, border: `1px solid ${agent.color}44` }}
                      />
                    ))}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
