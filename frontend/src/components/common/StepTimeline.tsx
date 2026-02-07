import React from 'react';
import { Box, Paper, Typography, Stepper, Step, StepLabel, StepContent } from '@mui/material';
import { AgentStep } from '../../types';

interface StepTimelineProps {
  steps: AgentStep[];
  title?: string;
}

export default function StepTimeline({ steps, title }: StepTimelineProps) {
  return (
    <Paper sx={{ p: 2 }}>
      {title && <Typography variant="h6" gutterBottom>{title}</Typography>}
      <Stepper orientation="vertical" activeStep={steps.length - 1}>
        {steps.map((step) => (
          <Step key={step.id} completed={step.status === 'completed'}>
            <StepLabel
              error={step.status === 'failed'}
              optional={
                <Typography variant="caption" color="text.secondary">
                  {step.output_state?.action as string || ''}
                  {step.duration_ms ? ` (${step.duration_ms}ms)` : ''}
                </Typography>
              }
            >
              {step.node_name}
            </StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                Step {step.step_number} - {step.status}
              </Typography>
              {step.output_state && (
                <Box
                  sx={{
                    mt: 1,
                    p: 1,
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    borderRadius: 1,
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                    maxHeight: 150,
                    overflow: 'auto',
                  }}
                >
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(step.output_state, null, 2)}
                  </pre>
                </Box>
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
}
