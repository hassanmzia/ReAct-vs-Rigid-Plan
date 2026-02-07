import React from 'react';
import { Chip } from '@mui/material';

interface AgentTypeChipProps {
  type: string;
}

const AGENT_COLORS: Record<string, string> = {
  react: '#4CAF50',
  rigid: '#FF9800',
  multi: '#9C27B0',
  recursive: '#2196F3',
};

const AGENT_LABELS: Record<string, string> = {
  react: 'ReAct',
  rigid: 'Rigid',
  multi: 'Multi-Agent',
  recursive: 'Recursive Q&A',
};

export default function AgentTypeChip({ type }: AgentTypeChipProps) {
  return (
    <Chip
      label={AGENT_LABELS[type] || type}
      size="small"
      sx={{
        backgroundColor: `${AGENT_COLORS[type] || '#666'}22`,
        color: AGENT_COLORS[type] || '#666',
        borderColor: AGENT_COLORS[type] || '#666',
        border: '1px solid',
      }}
    />
  );
}
