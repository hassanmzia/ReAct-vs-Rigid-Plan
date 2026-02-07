import React, { useState } from 'react';
import {
  Box, Grid, Typography, TextField, Button, Card, CardContent,
  CircularProgress, Alert, Slider, LinearProgress, Paper,
} from '@mui/material';
import { Psychology } from '@mui/icons-material';
import { agentApi } from '../services/api';
import { AgentSession } from '../types';
import MermaidDiagram from '../components/common/MermaidDiagram';
import StepTimeline from '../components/common/StepTimeline';

export default function RecursiveQAPage() {
  const [query, setQuery] = useState('What are the key differences between ReAct and Plan-and-Execute agent architectures, and when should each be used?');
  const [maxRefinements, setMaxRefinements] = useState(3);
  const [targetConfidence, setTargetConfidence] = useState(0.85);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentSession | null>(null);
  const [error, setError] = useState('');

  const handleRun = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const res = await agentApi.recursiveQA({
        query,
        max_refinements: maxRefinements,
        target_confidence: targetConfidence,
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Recursive QA failed');
    } finally {
      setLoading(false);
    }
  };

  const qaResult = result?.final_result as any;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Recursive Q&A Tuneup</Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Iteratively refine queries until high-confidence answers are achieved
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Card>
            <CardContent>
              <TextField
                fullWidth
                label="Your Question"
                multiline
                rows={4}
                value={query}
                onChange={e => setQuery(e.target.value)}
                sx={{ mb: 3 }}
              />

              <Typography gutterBottom>Max Refinements: {maxRefinements}</Typography>
              <Slider
                value={maxRefinements}
                onChange={(_, v) => setMaxRefinements(v as number)}
                min={1}
                max={10}
                step={1}
                marks
                sx={{ mb: 3 }}
              />

              <Typography gutterBottom>Target Confidence: {(targetConfidence * 100).toFixed(0)}%</Typography>
              <Slider
                value={targetConfidence}
                onChange={(_, v) => setTargetConfidence(v as number)}
                min={0.5}
                max={1.0}
                step={0.05}
                sx={{ mb: 3 }}
              />

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Psychology />}
                onClick={handleRun}
                disabled={loading || !query}
              >
                {loading ? 'Refining...' : 'Start Recursive Q&A'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={7}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {result && (
            <Box>
              {/* Confidence Summary */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="subtitle2">Final Confidence</Typography>
                    <Typography variant="h6" color="primary">
                      {((qaResult?.final_confidence || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(qaResult?.final_confidence || 0) * 100}
                    sx={{ height: 8, borderRadius: 4, mb: 1 }}
                    color={
                      (qaResult?.final_confidence || 0) >= targetConfidence
                        ? 'success'
                        : 'warning'
                    }
                  />
                  <Typography variant="caption" color="text.secondary">
                    {qaResult?.total_iterations || 0} iterations completed | Target: {(targetConfidence * 100).toFixed(0)}%
                  </Typography>
                </CardContent>
              </Card>

              {/* Final Answer */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Final Answer</Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {qaResult?.final_answer || 'No answer generated'}
                  </Typography>
                </CardContent>
              </Card>

              {/* Refinement History */}
              {qaResult?.refinement_history?.length > 0 && (
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Refinement History</Typography>
                    {qaResult.refinement_history.map((entry: any, i: number) => (
                      <Paper
                        key={i}
                        sx={{ p: 2, mb: 2, backgroundColor: 'rgba(0,0,0,0.2)' }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle2">Iteration {entry.iteration}</Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: entry.confidence >= targetConfidence ? '#4CAF50' : '#FF9800',
                              fontWeight: 600,
                            }}
                          >
                            {(entry.confidence * 100).toFixed(1)}%
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Query: {entry.query}
                        </Typography>
                        {entry.refinement_suggestion && (
                          <Typography variant="caption" color="warning.main" display="block" sx={{ mt: 0.5 }}>
                            Refinement: {entry.refinement_suggestion}
                          </Typography>
                        )}
                      </Paper>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Steps & Graph */}
              {result.steps?.length > 0 && <StepTimeline steps={result.steps} title="Execution Steps" />}
              {result.graph_definition?.mermaid && (
                <Box sx={{ mt: 2 }}>
                  <MermaidDiagram chart={result.graph_definition.mermaid} title="Recursive Q&A Graph" />
                </Box>
              )}
            </Box>
          )}
        </Grid>
      </Grid>
    </Box>
  );
}
