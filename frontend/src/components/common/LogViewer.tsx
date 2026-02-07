import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

interface LogEntry {
  level: string;
  time: string;
  message: string;
}

interface LogViewerProps {
  logs: LogEntry[];
  title?: string;
}

const LEVEL_COLORS: Record<string, string> = {
  INFO: '#4CAF50',
  WARNING: '#FF9800',
  ERROR: '#f44336',
  DEBUG: '#9E9E9E',
};

export default function LogViewer({ logs, title }: LogViewerProps) {
  return (
    <Paper sx={{ p: 2 }}>
      {title && <Typography variant="h6" gutterBottom>{title}</Typography>}
      <Box
        sx={{
          fontFamily: 'monospace',
          fontSize: '0.85rem',
          maxHeight: 400,
          overflow: 'auto',
          backgroundColor: '#0a0a15',
          borderRadius: 1,
          p: 2,
        }}
      >
        {logs.length === 0 ? (
          <Typography color="text.secondary" variant="body2">No logs available</Typography>
        ) : (
          logs.map((log, i) => (
            <Box key={i} sx={{ mb: 0.5, display: 'flex', gap: 1 }}>
              <Box
                component="span"
                sx={{ color: LEVEL_COLORS[log.level] || '#999', minWidth: 70 }}
              >
                [{log.level}]
              </Box>
              <Box component="span" sx={{ color: '#888' }}>{log.time}</Box>
              <Box component="span" sx={{ color: '#ddd' }}>{log.message}</Box>
            </Box>
          ))
        )}
      </Box>
    </Paper>
  );
}
