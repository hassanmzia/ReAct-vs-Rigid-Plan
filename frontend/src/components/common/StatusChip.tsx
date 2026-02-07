import React from 'react';
import { Chip } from '@mui/material';

interface StatusChipProps {
  status: string;
}

const STATUS_COLORS: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  completed: 'success',
  running: 'info',
  pending: 'warning',
  failed: 'error',
  cancelled: 'default',
};

export default function StatusChip({ status }: StatusChipProps) {
  return (
    <Chip
      label={status}
      color={STATUS_COLORS[status] || 'default'}
      size="small"
      variant="outlined"
    />
  );
}
