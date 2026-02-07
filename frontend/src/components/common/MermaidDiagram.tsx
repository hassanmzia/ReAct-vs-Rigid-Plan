import React, { useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
  title?: string;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    primaryColor: '#6C63FF',
    primaryTextColor: '#fff',
    primaryBorderColor: '#6C63FF',
    lineColor: '#aaa',
    secondaryColor: '#1A1A2E',
    tertiaryColor: '#16213E',
  },
});

let diagramCounter = 0;

export default function MermaidDiagram({ chart, title }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !chart) return;

    const id = `mermaid-${++diagramCounter}`;
    containerRef.current.innerHTML = '';

    mermaid.render(id, chart).then(({ svg }) => {
      if (containerRef.current) {
        containerRef.current.innerHTML = svg;
      }
    }).catch((err) => {
      console.error('Mermaid render error:', err);
      if (containerRef.current) {
        containerRef.current.innerHTML = `<pre style="color: #f44336">${chart}</pre>`;
      }
    });
  }, [chart]);

  return (
    <Paper sx={{ p: 2 }}>
      {title && (
        <Typography variant="h6" gutterBottom>{title}</Typography>
      )}
      <Box
        ref={containerRef}
        sx={{
          display: 'flex',
          justifyContent: 'center',
          '& svg': { maxWidth: '100%', height: 'auto' },
        }}
      />
    </Paper>
  );
}
