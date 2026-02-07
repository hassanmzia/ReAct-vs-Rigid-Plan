# AI Recursive Q&A Tuneup - ReAct vs Rigid Plan-and-Execute

A professional-grade multi-agent AI application that implements and compares **Adaptive ReAct** vs **Rigid Plan-and-Execute** agent architectures using **LangGraph**, with recursive Q&A refinement, multi-agent orchestration, MCP tools, and A2A protocol support.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                │
│                    http://172.168.1.95:3081                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │Dashboard │ │Agent Run │ │Compare  │ │Recursive Q&A    │   │
│  │Analytics │ │& Results │ │Side-by- │ │Tuneup Interface │   │
│  └──────────┘ └──────────┘ │Side     │ └──────────────────┘  │
│  ┌──────────┐ ┌──────────┐ └──────────┘ ┌──────────────────┐  │
│  │Documents │ │Graph Viz │ ┌──────────┐ │MCP & A2A Panels │   │
│  │Manager  │ │(Mermaid) │ │Contacts │ └──────────────────┘  │
│  └──────────┘ └──────────┘ └──────────┘                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST + WebSocket
┌────────────────────────────┴────────────────────────────────────┐
│              Backend (Django + DRF + Channels)                  │
│              http://172.168.1.95:8042                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   LangGraph Agents                       │   │
│  │  ┌───────────┐ ┌───────────┐ ┌─────────────────────┐   │   │
│  │  │ ReAct     │ │ Rigid     │ │ Multi-Agent          │   │   │
│  │  │ Agent     │ │ Agent     │ │ Orchestrator         │   │   │
│  │  └───────────┘ └───────────┘ └─────────────────────┘   │   │
│  │  ┌───────────────────┐  ┌──────────────────────────┐   │   │
│  │  │ Recursive Q&A     │  │ Graph Visualizer         │   │   │
│  │  │ Tuneup Service    │  │ (Mermaid + JSON)         │   │   │
│  │  └───────────────────┘  └──────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │MCP Tools │ │A2A Proto │ │Doc RAG  │ │Analytics Engine │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │Celery   │ │LangSmith │ │Langfuse │                        │
│  │Workers  │ │Tracing   │ │Monitor  │                        │
│  └──────────┘ └──────────┘ └──────────┘                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
┌────┴─────┐          ┌─────┴──────┐          ┌─────┴──────┐
│PostgreSQL│          │   Redis    │          │  Flower    │
│ :5433    │          │   :6380    │          │  :5556     │
└──────────┘          └────────────┘          └────────────┘
```

## Features

### Core Agent Architectures (from Notebook)
- **Adaptive ReAct Agent**: Conditional routing, LLM disambiguation, retry loops
- **Rigid Plan-and-Execute Agent**: Fixed sequential workflow, no retry
- **Side-by-Side Comparison**: Run both agents on the same task, see who wins

### Extended Features
- **Multi-Agent Orchestrator**: Supervisor coordinating Research, Reasoning, and Action agents
- **Recursive Q&A Tuneup**: Iterative query refinement with confidence scoring
- **Document Processing (RAG)**: Upload PDFs, extract text, chunk for retrieval
- **MCP Tools**: Model Context Protocol tool server for external AI integration
- **A2A Protocol**: Agent-to-Agent discovery, messaging, and task delegation
- **LangGraph Visualization**: Interactive Mermaid diagrams of all agent workflows
- **Real-time Updates**: WebSocket-based live execution streaming
- **Analytics Dashboard**: Performance metrics, trends, and agent leaderboard
- **LangSmith Integration**: Full execution tracing and debugging
- **Langfuse Integration**: Observability and monitoring

### Technology Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Material UI, Mermaid, Recharts |
| Backend | Django 5.1, Django REST Framework, Django Channels |
| AI/ML | LangChain, LangGraph, OpenAI GPT-4o-mini |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| Task Queue | Celery 5 with Beat scheduler |
| Observability | LangSmith, Langfuse, Flower |
| Infrastructure | Docker Compose, Nginx |

## Quick Start

### 1. Clone and Configure

```bash
cp .env.example .env
# Edit .env with your API keys (OPENAI_API_KEY is required)
```

### 2. Launch with Docker Compose

```bash
docker compose up --build -d
```

### 3. Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://172.168.1.95:3081 |
| Backend API | http://172.168.1.95:8042/api/ |
| Django Admin | http://172.168.1.95:8042/admin/ |
| Flower Monitor | http://172.168.1.95:5556 |
| API Health | http://172.168.1.95:8042/api/health/ |

## Port Configuration

All ports are non-default to avoid conflicts in multi-host environments:

| Service | Port | Default Would Be |
|---------|------|-------------------|
| Frontend (Nginx) | 3081 | 80/3000 |
| Backend (Django) | 8042 | 8000 |
| PostgreSQL | 5433 | 5432 |
| Redis | 6380 | 6379 |
| Flower | 5556 | 5555 |

## API Endpoints

### Agents
- `POST /api/agents/sessions/run-sync/` - Run agent synchronously
- `POST /api/agents/sessions/compare-sync/` - Compare ReAct vs Rigid
- `POST /api/agents/sessions/recursive-qa-sync/` - Recursive Q&A
- `GET /api/agents/sessions/` - List all sessions
- `GET /api/agents/sessions/{id}/` - Session detail

### Graphs
- `GET /api/agents/graph/?agent_type=react&format=mermaid` - Agent graph
- `GET /api/agents/graphs/` - All agent graphs

### Documents
- `POST /api/documents/` - Upload document
- `GET /api/documents/search/?q=query` - Search documents

### Analytics
- `GET /api/analytics/dashboard/` - Dashboard stats
- `GET /api/analytics/trends/` - Performance trends
- `GET /api/analytics/leaderboard/` - Agent leaderboard

## Agent Comparison: ReAct vs Rigid

| Feature | ReAct | Rigid |
|---------|-------|-------|
| Ambiguity Handling | LLM disambiguation | Fails |
| Retry Logic | Adaptive loops | None |
| Routing | Conditional | Fixed sequential |
| Complexity | Higher | Lower |
| Predictability | Variable | Deterministic |
| Best For | Complex tasks | Simple workflows |
