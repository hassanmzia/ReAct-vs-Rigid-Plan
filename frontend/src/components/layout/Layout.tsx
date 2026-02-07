import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItemButton,
  ListItemIcon, ListItemText, IconButton, Divider, Chip,
} from '@mui/material';
import {
  Dashboard, PlayArrow, Compare, Psychology, History, Description,
  AccountTree, Contacts, Hub, SmartToy, Menu as MenuIcon,
  ChevronLeft,
} from '@mui/icons-material';

const DRAWER_WIDTH = 260;

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: <Dashboard /> },
  { label: 'Run Agent', path: '/run', icon: <PlayArrow /> },
  { label: 'Compare Agents', path: '/compare', icon: <Compare /> },
  { label: 'Recursive Q&A', path: '/recursive-qa', icon: <Psychology /> },
  { label: 'Sessions', path: '/sessions', icon: <History /> },
  { label: 'Documents', path: '/documents', icon: <Description /> },
  { label: 'Agent Graphs', path: '/graphs', icon: <AccountTree /> },
  { label: 'Contacts', path: '/contacts', icon: <Contacts /> },
  { label: 'MCP Tools', path: '/mcp', icon: <Hub /> },
  { label: 'A2A Agents', path: '/a2a', icon: <SmartToy /> },
];

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (t) => t.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 100%)',
          borderBottom: '1px solid rgba(108,99,255,0.3)',
        }}
      >
        <Toolbar>
          <IconButton color="inherit" onClick={() => setDrawerOpen(!drawerOpen)} edge="start" sx={{ mr: 2 }}>
            {drawerOpen ? <ChevronLeft /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            AI Recursive Q&A Tuneup
          </Typography>
          <Chip
            label="ReAct vs Rigid"
            color="primary"
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          />
          <Chip label="LangGraph" color="secondary" variant="outlined" size="small" />
        </Toolbar>
      </AppBar>

      <Drawer
        variant="persistent"
        open={drawerOpen}
        sx={{
          width: drawerOpen ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            background: '#12121F',
            borderRight: '1px solid rgba(255,255,255,0.06)',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 1 }}>
          <List>
            {NAV_ITEMS.map((item) => (
              <ListItemButton
                key={item.path}
                selected={location.pathname === item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  mx: 1,
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    background: 'rgba(108,99,255,0.15)',
                    '&:hover': { background: 'rgba(108,99,255,0.25)' },
                  },
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? '#6C63FF' : 'inherit', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            ))}
          </List>
          <Divider sx={{ my: 2, mx: 2 }} />
          <Box sx={{ px: 2, pb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Powered by LangChain, LangGraph, LangSmith, Langfuse
            </Typography>
          </Box>
        </Box>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: drawerOpen ? 0 : `-${DRAWER_WIDTH}px`,
          transition: 'margin 0.3s',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
