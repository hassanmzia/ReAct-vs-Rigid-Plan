import React, { useEffect, useState, useCallback } from 'react';
import {
  Box, Typography, Card, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, CircularProgress, IconButton, Tooltip, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid,
} from '@mui/material';
import { Delete, Edit, Add } from '@mui/icons-material';
import { contactApi } from '../services/api';
import { Contact } from '../types';

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editContact, setEditContact] = useState<Partial<Contact>>({});

  const loadContacts = useCallback(() => {
    contactApi.getAll()
      .then(res => setContacts(res.data?.results || []))
      .catch(() => setContacts([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadContacts(); }, [loadContacts]);

  const handleSave = async () => {
    try {
      if (editContact.id) {
        await contactApi.update(editContact.id, editContact);
      } else {
        await contactApi.create(editContact);
      }
      setDialogOpen(false);
      setEditContact({});
      loadContacts();
    } catch (err) {
      console.error('Save failed:', err);
    }
  };

  const handleDelete = async (id: number) => {
    await contactApi.delete(id);
    loadContacts();
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4">Contacts</Typography>
          <Typography variant="body1" color="text.secondary">
            Manage the contact database used by agents
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => { setEditContact({}); setDialogOpen(true); }}
        >
          Add Contact
        </Button>
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Role</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {contacts.map(contact => (
                <TableRow key={contact.id} hover>
                  <TableCell>{contact.name}</TableCell>
                  <TableCell>{contact.email}</TableCell>
                  <TableCell>{contact.department}</TableCell>
                  <TableCell>{contact.role}</TableCell>
                  <TableCell align="center">
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => { setEditContact(contact); setDialogOpen(true); }}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton size="small" color="error" onClick={() => handleDelete(contact.id)}>
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editContact.id ? 'Edit Contact' : 'Add Contact'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField fullWidth label="Name" value={editContact.name || ''} onChange={e => setEditContact({ ...editContact, name: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth label="Email" value={editContact.email || ''} onChange={e => setEditContact({ ...editContact, email: e.target.value })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Department" value={editContact.department || ''} onChange={e => setEditContact({ ...editContact, department: e.target.value })} />
            </Grid>
            <Grid item xs={6}>
              <TextField fullWidth label="Role" value={editContact.role || ''} onChange={e => setEditContact({ ...editContact, role: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
