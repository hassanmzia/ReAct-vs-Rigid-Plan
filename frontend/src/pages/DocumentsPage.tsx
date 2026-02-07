import React, { useEffect, useState, useCallback } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Tooltip, Alert,
} from '@mui/material';
import { CloudUpload, Delete, Search } from '@mui/icons-material';
import { documentApi } from '../services/api';
import { Document } from '../types';
import StatusChip from '../components/common/StatusChip';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadDocuments = useCallback(() => {
    documentApi.getAll()
      .then(res => setDocuments(res.data?.results || []))
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadDocuments(); }, [loadDocuments]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await documentApi.upload(file);
      loadDocuments();
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id);
      loadDocuments();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4">Documents</Typography>
          <Typography variant="body1" color="text.secondary">Upload and manage research papers for RAG</Typography>
        </Box>
        <Button
          variant="contained"
          component="label"
          startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
          disabled={uploading}
        >
          Upload Document
          <input type="file" hidden accept=".pdf,.txt,.md,.docx" onChange={handleUpload} />
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Size</TableCell>
                <TableCell align="right">Pages</TableCell>
                <TableCell align="right">Chunks</TableCell>
                <TableCell>Uploaded</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography color="text.secondary" sx={{ py: 4 }}>
                      No documents uploaded. Upload PDFs or text files to enable document-based Q&A.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                documents.map(doc => (
                  <TableRow key={doc.id} hover>
                    <TableCell>{doc.title}</TableCell>
                    <TableCell>{doc.doc_type.toUpperCase()}</TableCell>
                    <TableCell><StatusChip status={doc.processing_status} /></TableCell>
                    <TableCell align="right">{formatSize(doc.file_size)}</TableCell>
                    <TableCell align="right">{doc.page_count || '-'}</TableCell>
                    <TableCell align="right">{doc.chunk_count}</TableCell>
                    <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Delete">
                        <IconButton size="small" onClick={() => handleDelete(doc.id)} color="error">
                          <Delete />
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
