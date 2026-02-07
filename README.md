# ReAct vs Rigid Plan - AI Recursive Q&A Tuneup

A production-grade multi-agent AI application that implements and compares four distinct agent architectures using **LangGraph** and **LangChain**, with a full-stack Django + React interface, real-time execution streaming, document RAG, and comprehensive observability.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [System Architecture Diagram](#system-architecture-diagram)
  - [Component Overview](#component-overview)
  - [Data Flow](#data-flow)
- [Agent Architectures](#agent-architectures)
  - [1. Adaptive ReAct Agent](#1-adaptive-react-agent)
  - [2. Rigid Plan-and-Execute Agent](#2-rigid-plan-and-execute-agent)
  - [3. Multi-Agent Orchestrator](#3-multi-agent-orchestrator)
  - [4. Recursive Q&A Tuneup](#4-recursive-qa-tuneup)
  - [Agent Comparison Matrix](#agent-comparison-matrix)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Docker Infrastructure](#docker-infrastructure)
- [API Reference](#api-reference)
  - [Agent Endpoints](#agent-endpoints)
  - [Graph Visualization Endpoints](#graph-visualization-endpoints)
  - [Contact Endpoints](#contact-endpoints)
  - [Document Endpoints](#document-endpoints)
  - [Analytics Endpoints](#analytics-endpoints)
  - [WebSocket Endpoints](#websocket-endpoints)
- [Frontend Pages](#frontend-pages)
- [Backend Services](#backend-services)
- [Database Models](#database-models)
- [Advanced Features](#advanced-features)
  - [MCP (Model Context Protocol)](#mcp-model-context-protocol)
  - [A2A (Agent-to-Agent Protocol)](#a2a-agent-to-agent-protocol)
  - [Document Processing & RAG](#document-processing--rag)
  - [LangGraph Visualization](#langgraph-visualization)
  - [Real-time Execution Streaming](#real-time-execution-streaming)
  - [Observability & Tracing](#observability--tracing)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [Port Configuration](#port-configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

This application serves as a comprehensive platform for comparing different AI agent architectures built on LangGraph. It demonstrates the trade-offs between adaptive reasoning (ReAct), deterministic planning (Rigid), multi-agent coordination, and iterative refinement (Recursive Q&A) through a real-world corporate email workflow scenario.

**Key capabilities:**

- Execute and compare four distinct LangGraph agent architectures side-by-side
- Real-time WebSocket streaming of agent execution steps
- Interactive LangGraph workflow visualization using Mermaid diagrams
- Document upload with PDF extraction and RAG-powered Q&A
- MCP tool server for external AI system integration
- A2A protocol for inter-agent discovery and communication
- Full analytics dashboard with performance metrics and trends
- Asynchronous task processing via Celery with Flower monitoring
- Production observability through LangSmith and Langfuse integration

---

## Architecture

### System Architecture Diagram

```
                         ┌──────────────────────────────────┐
                         │          Client Browser           │
                         └───────────────┬──────────────────┘
                                         │
                         ┌───────────────┴──────────────────┐
                         │   Frontend (Nginx + React 18)     │
                         │   Port 3081                       │
                         │                                   │
                         │  Pages: Dashboard, Agent Runner,  │
                         │  Comparison, Recursive Q&A,       │
                         │  Sessions, Documents, Graphs,     │
                         │  Contacts, MCP, A2A               │
                         │                                   │
                         │  Components: MermaidDiagram,       │
                         │  LogViewer, StepTimeline           │
                         └──────┬──────────────┬─────────────┘
                                │ REST API     │ WebSocket
                         ┌──────┴──────────────┴─────────────┐
                         │   Backend (Daphne ASGI + Django)   │
                         │   Port 8042                        │
                         │                                    │
                         │  ┌──────────────────────────────┐  │
                         │  │      Django REST Framework    │  │
                         │  │  ViewSets: Contact, Session,  │  │
                         │  │  Comparison, Graph, Document  │  │
                         │  └──────────────┬───────────────┘  │
                         │                 │                   │
                         │  ┌──────────────┴───────────────┐  │
                         │  │      LangGraph Agent Engine   │  │
                         │  │                               │  │
                         │  │  ┌─────────┐  ┌───────────┐  │  │
                         │  │  │  ReAct  │  │   Rigid   │  │  │
                         │  │  │  Agent  │  │   Agent   │  │  │
                         │  │  └─────────┘  └───────────┘  │  │
                         │  │  ┌─────────┐  ┌───────────┐  │  │
                         │  │  │  Multi  │  │ Recursive │  │  │
                         │  │  │  Agent  │  │    Q&A    │  │  │
                         │  │  └─────────┘  └───────────┘  │  │
                         │  └──────────────────────────────┘  │
                         │                                    │
                         │  ┌────────────┐  ┌──────────────┐  │
                         │  │ MCP Service│  │ A2A Service  │  │
                         │  └────────────┘  └──────────────┘  │
                         │  ┌────────────┐  ┌──────────────┐  │
                         │  │Doc Process │  │  Analytics   │  │
                         │  └────────────┘  └──────────────┘  │
                         └──┬──────────┬──────────┬───────────┘
                            │          │          │
              ┌─────────────┴──┐  ┌────┴────┐  ┌──┴──────────┐
              │  Celery Worker │  │  Celery │  │   Flower    │
              │  (4 workers)   │  │  Beat   │  │   :5557     │
              │  Queues:       │  │ Sched.  │  │  Monitoring │
              │  default,      │  └────┬────┘  └─────────────┘
              │  agents,       │       │
              │  documents     │       │
              └───────┬────────┘       │
                      │                │
         ┌────────────┴────────┬───────┴──────────┐
         │                     │                   │
    ┌────┴──────┐       ┌─────┴──────┐     ┌──────┴──────┐
    │PostgreSQL │       │   Redis    │     │  OpenAI API │
    │  16       │       │   7        │     │  GPT-4o-mini│
    │  :5437    │       │   :6383    │     └─────────────┘
    │           │       │            │     ┌─────────────┐
    │ Models:   │       │ - Cache    │     │  LangSmith  │
    │ Contact   │       │ - Channels │     │  Tracing    │
    │ Session   │       │ - Broker   │     └─────────────┘
    │ Step      │       │            │     ┌─────────────┐
    │ Query     │       │            │     │  Langfuse   │
    │ Document  │       │            │     │  Monitoring │
    └───────────┘       └────────────┘     └─────────────┘
```

### Component Overview

| Layer | Component | Technology | Purpose |
|-------|-----------|------------|---------|
| **Frontend** | React SPA | React 18, TypeScript, MUI 6 | User interface with 11 pages |
| **Frontend** | Mermaid Renderer | Mermaid 11.3 | LangGraph workflow visualization |
| **Frontend** | WebSocket Client | Native WebSocket | Real-time execution streaming |
| **Web Server** | Nginx | Nginx Alpine | Static file serving, reverse proxy |
| **Backend** | Django API | Django 5.1, DRF 3.15 | REST API and business logic |
| **Backend** | Daphne ASGI | Daphne 4.1 | HTTP + WebSocket server |
| **Backend** | Django Channels | Channels 4.1 | WebSocket consumers |
| **Agents** | LangGraph Engine | LangGraph 0.2, LangChain 0.3 | Agent workflow orchestration |
| **Agents** | OpenAI Integration | langchain-openai 0.3 | LLM inference (GPT-4o-mini) |
| **Queue** | Celery Worker | Celery 5.4 | Async task processing |
| **Queue** | Celery Beat | celery-beat 2.6 | Scheduled task execution |
| **Queue** | Flower | Flower 2.0 | Task queue monitoring UI |
| **Data** | PostgreSQL | PostgreSQL 16 | Persistent data storage |
| **Data** | Redis | Redis 7 | Cache, channel layer, message broker |
| **Observability** | LangSmith | langsmith 0.1 | LLM execution tracing |
| **Observability** | Langfuse | langfuse 2.0 | Production monitoring |

### Data Flow

**Synchronous Agent Execution:**
```
User Input → React Frontend → POST /api/agents/sessions/run-sync/
  → Django View → AgentService.run() → LangGraph.invoke()
    → Node 1 (e.g., react_node) → OpenAI API → Node 2 → ... → END
  → Response with session data, steps, logs ← Frontend renders results
```

**Asynchronous Agent Execution:**
```
User Input → POST /api/agents/sessions/run/
  → Celery task queued → 202 Accepted returned immediately
  → Celery Worker picks up task → Executes LangGraph workflow
  → WebSocket pushes real-time updates → Frontend renders live
  → Task completes → Session updated in database
```

**Document RAG Flow:**
```
File Upload → POST /api/documents/
  → PDF/TXT/DOCX extraction → Text chunking (1000 chars, 200 overlap)
  → Token counting → Chunks stored in DocumentChunk model
  → Available as context for Recursive Q&A agent
```

---

## Agent Architectures

### 1. Adaptive ReAct Agent

The ReAct (Reason + Act) agent implements adaptive routing with LLM-based disambiguation and retry logic. It handles ambiguous scenarios by using the LLM to resolve conflicts.

**Workflow Graph:**
```
START → react_node → [approve] → email_node → END
                   → [fail]    → contact_node → react_node (retry)
                   → [END]     → END
```

**Key characteristics:**
- **Conditional routing** based on contact lookup results (single match, ambiguous, not found)
- **LLM disambiguation** when multiple contacts match a query
- **Retry loop** with configurable max retries (default: 5)
- **Structured output** using Pydantic models for reliable LLM responses
- Handles edge cases gracefully through adaptive reasoning

**LangGraph nodes:**
| Node | Purpose | Routing |
|------|---------|---------|
| `react_node` | Contact lookup with reasoning | Conditional: approve/fail/END |
| `contact_node` | LLM-based ambiguity resolution | Always → react_node |
| `email_node` | LLM email generation | Always → END |

### 2. Rigid Plan-and-Execute Agent

The Rigid agent follows a fixed, deterministic sequential workflow. It generates a plan upfront and executes each step in order without any retry or adaptation capability.

**Workflow Graph:**
```
START → planner → contacts → email → END
```

**Key characteristics:**
- **Fixed sequential plan** generated at the start
- **No retry logic** - fails immediately on ambiguous results
- **Deterministic execution** - same input always produces the same flow
- **Lower complexity** - simpler to understand and debug
- Suitable for well-defined, unambiguous tasks

**LangGraph nodes:**
| Node | Purpose | Routing |
|------|---------|---------|
| `planner` | Creates fixed execution plan | Sequential → contacts |
| `contacts` | Database lookup (no disambiguation) | Sequential → email |
| `email` | Send email (fails if contact lookup failed) | Sequential → END |

### 3. Multi-Agent Orchestrator

A supervisor-based architecture that coordinates multiple specialized agents, implementing A2A (Agent-to-Agent) communication patterns.

**Workflow Graph:**
```
START → supervisor → [research]   → research_agent → supervisor
                   → [reasoning]  → reasoning_agent → supervisor
                   → [action]     → action_agent → supervisor
                   → [synthesize] → synthesizer → END
```

**Key characteristics:**
- **Supervisor pattern** orchestrating workflow phases
- **Specialized agents** (Research, Reasoning, Action) with distinct roles
- **A2A message logging** for inter-agent communication tracking
- **Sequential phase execution**: research → reasoning → action → synthesis
- Demonstrates multi-agent coordination patterns

**Agent roles:**
| Agent | Role | Capability |
|-------|------|------------|
| Supervisor | Workflow orchestrator | Routes to appropriate agent |
| Research Agent | Information gathering | Contextual research on queries |
| Reasoning Agent | Analysis & synthesis | Structured analytical reasoning |
| Action Agent | Task execution | Concrete action descriptions |
| Synthesizer | Final output | Combines all agent outputs |

### 4. Recursive Q&A Tuneup

An iterative refinement agent that generates answers, evaluates their quality, and recursively refines the query until a confidence threshold is met.

**Workflow Graph:**
```
START → answer → evaluate → [refine] → refine → answer (loop)
                           → [end]   → END
```

**Key characteristics:**
- **Iterative refinement loop** with configurable max iterations (default: 3)
- **Confidence scoring** (0.0-1.0) using structured LLM evaluation
- **Quality dimensions**: completeness, accuracy, clarity, relevance
- **Query optimization** based on evaluation feedback
- **Document context** support for RAG-powered answers
- **Full iteration history** tracking for transparency

**Configuration parameters:**
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `max_refinements` | 3 | 1-10 | Maximum refinement iterations |
| `target_confidence` | 0.85 | 0.0-1.0 | Confidence threshold to stop |

### Agent Comparison Matrix

| Feature | ReAct | Rigid | Multi-Agent | Recursive Q&A |
|---------|-------|-------|-------------|---------------|
| **Pattern** | Adaptive reasoning | Fixed plan | Supervisor delegation | Iterative refinement |
| **Routing** | Conditional (LLM) | Sequential | Supervisor-controlled | Confidence-based |
| **Retry Logic** | Yes (max 5) | None | Per-agent | Yes (max configurable) |
| **LLM Calls** | 1-3+ per run | 0 | 4 (one per agent) | 2-6+ per run |
| **Ambiguity Handling** | LLM disambiguation | Fails | Delegated to agents | Query refinement |
| **Deterministic** | No | Yes | No | No |
| **Complexity** | Medium | Low | High | Medium |
| **Best For** | Ambiguous tasks | Simple workflows | Complex multi-step | Knowledge Q&A |
| **Execution Time** | Variable | Fast | Slow (multiple LLM) | Variable |

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 4.9 | Type-safe JavaScript |
| Material-UI (MUI) | 6.1 | Component library |
| React Router | 6.26 | Client-side routing |
| Axios | 1.7 | HTTP client |
| Mermaid | 11.3 | Graph diagram rendering |
| Recharts | 2.13 | Data visualization charts |
| Notistack | 3.0 | Snackbar notifications |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 5.1 | Web framework |
| Django REST Framework | 3.15 | REST API toolkit |
| Django Channels | 4.1 | WebSocket support |
| Daphne | 4.1 | ASGI server |
| Celery | 5.4 | Async task queue |
| django-celery-beat | 2.6 | Periodic task scheduler |
| django-filter | 24.0 | API filtering |
| django-cors-headers | 4.4 | CORS middleware |

### AI / ML
| Technology | Version | Purpose |
|------------|---------|---------|
| LangChain | 0.3 | LLM application framework |
| LangGraph | 0.2 | Agent workflow graphs |
| langchain-openai | 0.3 | OpenAI LLM integration |
| OpenAI GPT-4o-mini | - | Default LLM model |
| Pydantic | 2.0 | Structured LLM output |
| tiktoken | 0.7 | Token counting |
| FAISS (CPU) | 1.8 | Vector similarity search |

### Infrastructure
| Technology | Version | Purpose |
|------------|---------|---------|
| Docker Compose | 3.9 | Container orchestration |
| PostgreSQL | 16 (Alpine) | Primary database |
| Redis | 7 (Alpine) | Cache, broker, channel layer |
| Nginx | Alpine | Frontend static server |
| Flower | 2.0 | Celery monitoring dashboard |

### Observability
| Technology | Version | Purpose |
|------------|---------|---------|
| LangSmith | 0.1 | LLM execution tracing |
| Langfuse | 2.0 | Production monitoring |
| Sentry SDK | 2.0 | Error tracking |

### Document Processing
| Technology | Version | Purpose |
|------------|---------|---------|
| pypdf | 4.0 | PDF text extraction |
| python-docx | 1.0 | DOCX file processing |
| unstructured | 0.15 | General document parsing |

---

## Project Structure

```
ReAct-vs-Rigid-Plan/
├── .env                          # Environment configuration
├── .env.example                  # Environment template
├── docker-compose.yml            # Docker Compose orchestration
├── README.md                     # This file
│
├── docs/                         # Documentation assets
│   ├── architecture.drawio       # Draw.io architecture diagram
│   └── Technical_Architecture.pptx  # PowerPoint presentation
│
├── backend/                      # Django backend application
│   ├── Dockerfile                # Python 3.12-slim container
│   ├── requirements.txt          # Python dependencies (50+ packages)
│   ├── manage.py                 # Django management script
│   │
│   ├── config/                   # Django project configuration
│   │   ├── settings.py           # Settings (DB, cache, DRF, CORS, AI)
│   │   ├── urls.py               # Root URL configuration
│   │   ├── asgi.py               # ASGI app (Daphne + Channels)
│   │   ├── wsgi.py               # WSGI app (fallback)
│   │   └── celery.py             # Celery app configuration
│   │
│   ├── agents/                   # Main agent orchestration app
│   │   ├── models.py             # Contact, AgentSession, AgentStep, etc.
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # ViewSets and API views
│   │   ├── urls.py               # Agent URL routing
│   │   ├── tasks.py              # Celery task definitions
│   │   ├── consumers.py          # WebSocket consumers
│   │   ├── routing.py            # WebSocket URL routing
│   │   ├── admin.py              # Django admin registration
│   │   │
│   │   ├── services/             # Agent service implementations
│   │   │   ├── react_agent.py    # Adaptive ReAct agent (LangGraph)
│   │   │   ├── rigid_agent.py    # Rigid Plan-and-Execute agent
│   │   │   ├── multi_agent.py    # Multi-Agent Orchestrator
│   │   │   ├── recursive_qa.py   # Recursive Q&A Tuneup service
│   │   │   ├── graph_visualizer.py  # Mermaid diagram generator
│   │   │   ├── mcp_service.py    # Model Context Protocol service
│   │   │   └── a2a_service.py    # Agent-to-Agent protocol service
│   │   │
│   │   └── management/
│   │       └── commands/
│   │           └── seed_contacts.py  # Database seeding command
│   │
│   ├── documents/                # Document processing app
│   │   ├── models.py             # Document, DocumentChunk models
│   │   ├── serializers.py        # Document serializers
│   │   ├── views.py              # Document upload/management views
│   │   ├── urls.py               # Document URL routing
│   │   └── services/
│   │       └── pdf_processor.py  # PDF extraction and chunking
│   │
│   └── analytics/                # Analytics and metrics app
│       ├── models.py             # (Computed from agent models)
│       ├── views.py              # Dashboard, trends, leaderboard
│       └── urls.py               # Analytics URL routing
│
├── frontend/                     # React TypeScript frontend
│   ├── Dockerfile                # Node 18 → Nginx Alpine
│   ├── package.json              # NPM dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   │
│   └── src/
│       ├── App.tsx               # Root app with routing and theme
│       ├── index.tsx             # React entry point
│       │
│       ├── types/
│       │   └── index.ts          # TypeScript interfaces
│       │
│       ├── services/
│       │   ├── api.ts            # Axios API client (all endpoints)
│       │   └── websocket.ts      # WebSocket service
│       │
│       ├── pages/
│       │   ├── DashboardPage.tsx     # Analytics overview
│       │   ├── AgentRunnerPage.tsx   # Single agent execution
│       │   ├── ComparisonPage.tsx    # ReAct vs Rigid comparison
│       │   ├── RecursiveQAPage.tsx   # Recursive Q&A interface
│       │   ├── SessionsPage.tsx      # Session history list
│       │   ├── SessionDetailPage.tsx # Session detail view
│       │   ├── DocumentsPage.tsx     # Document management
│       │   ├── GraphsPage.tsx        # LangGraph visualization
│       │   ├── ContactsPage.tsx      # Contact database viewer
│       │   ├── MCPPage.tsx           # MCP tools panel
│       │   └── A2APage.tsx           # A2A communication panel
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   └── Layout.tsx        # Navigation sidebar layout
│       │   └── common/
│       │       ├── MermaidDiagram.tsx # Mermaid graph renderer
│       │       ├── LogViewer.tsx      # Execution log viewer
│       │       ├── StepTimeline.tsx   # Step-by-step timeline
│       │       ├── StatusChip.tsx     # Status badge component
│       │       └── AgentTypeChip.tsx  # Agent type badge
│       │
│       └── hooks/                # Custom React hooks (extensible)
│
├── nginx/                        # Nginx configuration (extensible)
└── research_papers/              # Research paper storage
```

---

## Getting Started

### Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **OpenAI API key** (required for agent execution)
- Minimum **4 GB RAM** available for Docker
- Ports 3081, 8042, 5437, 6383, 5557 available

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ReAct-vs-Rigid-Plan
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure your API key:**
   Edit `.env` and set your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

### Configuration

Edit `.env` to customize these settings:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for LLM inference |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API base URL (for proxies) |
| `DJANGO_DEBUG` | No | `1` | Debug mode (set to `0` in production) |
| `LANGCHAIN_TRACING_V2` | No | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | - | LangSmith API key |
| `LANGFUSE_PUBLIC_KEY` | No | - | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | No | - | Langfuse secret key |
| `MCP_ENABLED` | No | `true` | Enable MCP tool server |
| `A2A_ENABLED` | No | `true` | Enable A2A protocol |

### Running the Application

**Start all services:**
```bash
docker compose up --build -d
```

**Check service health:**
```bash
docker compose ps
```

**View logs:**
```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Specific agent execution logs
docker compose logs -f backend | grep -E "(react_node|plan_node|evaluate_node)"
```

**Stop all services:**
```bash
docker compose down
```

**Reset database:**
```bash
docker compose down -v   # Removes volumes
docker compose up --build -d
```

**Access the application:**

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3081 |
| Backend API Root | http://localhost:8042/api/ |
| Django Admin | http://localhost:8042/admin/ |
| Flower (Celery Monitor) | http://localhost:5557 |
| Health Check | http://localhost:8042/api/health/ |

> **Note:** Replace `localhost` with your host IP (e.g., `172.168.1.95`) when accessing from other machines.

---

## Docker Infrastructure

The application runs as 7 containerized services orchestrated by Docker Compose:

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                     Network: app_network (bridge)           │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ frontend │  │ backend  │  │ celery   │  │ celery   │   │
│  │ (nginx)  │  │ (daphne) │  │ _worker  │  │ _beat    │   │
│  │ :3081    │  │ :8042    │  │ 4 procs  │  │ sched.   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ postgres │  │  redis   │  │  flower  │                  │
│  │ :5437    │  │  :6383   │  │  :5557   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                                             │
│  Volumes: postgres_data, redis_data,                        │
│           static_volume, media_volume                       │
└─────────────────────────────────────────────────────────────┘
```

| Service | Container | Image | Internal Port | External Port |
|---------|-----------|-------|---------------|---------------|
| Frontend | `rr_frontend` | Node 18 → Nginx Alpine | 80 | 3081 |
| Backend | `rr_backend` | Python 3.12-slim | 8000 | 8042 |
| Celery Worker | `rr_celery_worker` | Python 3.12-slim | - | - |
| Celery Beat | `rr_celery_beat` | Python 3.12-slim | - | - |
| Flower | `rr_flower` | Python 3.12-slim | 5555 | 5557 |
| PostgreSQL | `rr_postgres` | PostgreSQL 16 Alpine | 5432 | 5437 |
| Redis | `rr_redis` | Redis 7 Alpine | 6379 | 6383 |

**Startup sequence:**
1. PostgreSQL and Redis start with health checks
2. Backend waits for healthy DB/Redis, then runs migrations and seeds contacts
3. Celery Worker and Beat connect to Redis broker
4. Frontend is built and served via Nginx

---

## API Reference

Base URL: `http://localhost:8042/api`

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/agents/sessions/run-sync/` | Run agent synchronously |
| `POST` | `/agents/sessions/run/` | Run agent asynchronously (Celery) |
| `POST` | `/agents/sessions/compare-sync/` | Compare ReAct vs Rigid |
| `POST` | `/agents/sessions/compare/` | Compare asynchronously |
| `POST` | `/agents/sessions/recursive-qa-sync/` | Recursive Q&A synchronous |
| `POST` | `/agents/sessions/recursive-qa/` | Recursive Q&A asynchronous |
| `GET` | `/agents/sessions/` | List all sessions (paginated) |
| `GET` | `/agents/sessions/{id}/` | Session detail with steps and logs |

**Run Agent Request:**
```json
{
  "agent_type": "react",
  "message": "Send a budget email to Alice",
  "user_name": "Alice",
  "max_iterations": 5
}
```

**Compare Agents Request:**
```json
{
  "message": "Send a budget email to Alice",
  "user_name": "Alice"
}
```

**Recursive Q&A Request:**
```json
{
  "query": "What are the key differences between ReAct and Plan-and-Execute?",
  "max_refinements": 3,
  "target_confidence": 0.85
}
```

### Graph Visualization Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/agents/graphs/` | All agent graphs (Mermaid) |
| `GET` | `/agents/graphs/?output_format=json` | All agent graphs (JSON) |
| `GET` | `/agents/graphs/{agent_type}/` | Single agent graph |

### Contact Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/agents/contacts/` | List all contacts |
| `POST` | `/agents/contacts/` | Create contact |
| `GET` | `/agents/contacts/{id}/` | Contact detail |
| `PUT` | `/agents/contacts/{id}/` | Update contact |
| `DELETE` | `/agents/contacts/{id}/` | Delete contact |

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/documents/` | List all documents |
| `POST` | `/documents/` | Upload document (multipart) |
| `GET` | `/documents/{id}/` | Document detail |
| `DELETE` | `/documents/{id}/` | Delete document |
| `POST` | `/documents/{id}/reprocess/` | Reprocess document |
| `GET` | `/documents/{id}/chunks/` | Get document chunks |
| `GET` | `/documents/search/?q=query` | Search documents |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/dashboard/` | Dashboard statistics |
| `GET` | `/analytics/trends/?days=7` | Performance trends |
| `GET` | `/analytics/leaderboard/` | Agent performance ranking |

### WebSocket Endpoints

| Protocol | Endpoint | Description |
|----------|----------|-------------|
| `ws://` | `/ws/agent/{session_id}/` | Live agent execution updates |
| `ws://` | `/ws/dashboard/` | Real-time dashboard stats |

---

## Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | Overview with analytics, charts, success rates, agent distribution |
| **Agent Runner** | `/agent-runner` | Execute individual agents with custom parameters |
| **Comparison** | `/comparison` | Side-by-side ReAct vs Rigid comparison with metrics |
| **Recursive Q&A** | `/recursive-qa` | Iterative Q&A with confidence tracking and refinement history |
| **Sessions** | `/sessions` | Filterable list of all agent execution sessions |
| **Session Detail** | `/sessions/:id` | Detailed view with step timeline, logs, and results |
| **Documents** | `/documents` | Upload, manage, and search documents for RAG |
| **Graphs** | `/graphs` | Interactive Mermaid diagrams for all 4 agent architectures |
| **Contacts** | `/contacts` | Corporate contact database CRUD interface |
| **MCP** | `/mcp` | Model Context Protocol tool registry and testing |
| **A2A** | `/a2a` | Agent-to-Agent communication protocol interface |

---

## Backend Services

### Agent Services (`backend/agents/services/`)

| Service | File | Description |
|---------|------|-------------|
| **ReactAgentService** | `react_agent.py` | Adaptive ReAct agent with conditional routing and LLM disambiguation |
| **RigidAgentService** | `rigid_agent.py` | Fixed plan-and-execute agent with sequential workflow |
| **MultiAgentOrchestrator** | `multi_agent.py` | Supervisor-based multi-agent system with A2A messaging |
| **RecursiveQAService** | `recursive_qa.py` | Iterative Q&A refinement with confidence evaluation |
| **GraphVisualizer** | `graph_visualizer.py` | Mermaid diagram and JSON graph generation for all agents |
| **MCPService** | `mcp_service.py` | Model Context Protocol tool server with 5 tools |
| **A2AService** | `a2a_service.py` | Agent-to-Agent discovery, messaging, and task delegation |

### Document Services (`backend/documents/services/`)

| Service | File | Description |
|---------|------|-------------|
| **DocumentProcessor** | `pdf_processor.py` | PDF/TXT/DOCX extraction, text chunking, token counting |

---

## Database Models

### Agents App

| Model | Key Fields | Description |
|-------|------------|-------------|
| **Contact** | name, email, department, role, is_active | Corporate contact directory |
| **AgentSession** | agent_type, status, user_message, execution_time_ms, retry_count | Agent execution session tracking |
| **AgentStep** | session, node_name, action, input_data, output_data, duration_ms | Individual LangGraph node traversal |
| **QueryHistory** | session, iteration, query, answer, confidence, is_satisfactory | Recursive Q&A refinement iterations |
| **AgentComparison** | react_session, rigid_session, winner, comparison_notes | Side-by-side comparison results |

### Documents App

| Model | Key Fields | Description |
|-------|------------|-------------|
| **Document** | title, file, doc_type, file_size, processing_status, extracted_text | Uploaded document metadata |
| **DocumentChunk** | document, chunk_index, content, page_number, token_count | Text chunks for RAG retrieval |

---

## Advanced Features

### MCP (Model Context Protocol)

The MCP service exposes agent capabilities as standardized tools for external AI systems:

| Tool Name | Description |
|-----------|-------------|
| `contact_lookup` | Search the corporate contact database |
| `run_react_agent` | Execute the Adaptive ReAct agent |
| `run_rigid_agent` | Execute the Rigid Plan-and-Execute agent |
| `recursive_qa` | Run Recursive Q&A with refinement |
| `compare_agents` | Run side-by-side agent comparison |

### A2A (Agent-to-Agent Protocol)

Implements agent discovery and inter-agent communication:

- **AgentCard**: Declares agent capabilities (name, description, skills)
- **A2AMessage**: Structured messages between agents (sender, receiver, content, timestamp)
- **A2AService**: Message routing and orchestration
- Default registered agents: ReAct Agent, Rigid Agent, Supervisor

### Document Processing & RAG

Upload documents that serve as context for the Recursive Q&A agent:

- **Supported formats**: PDF, TXT, DOCX, Markdown
- **Processing pipeline**: Extract text → Split into chunks (1000 chars, 200 overlap) → Count tokens
- **RAG integration**: Document chunks provided as context to the answer generation node
- **Max upload size**: 50 MB

### LangGraph Visualization

Each agent architecture has a Mermaid diagram definition accessible through the Graphs page:

- All four agent workflows rendered as interactive directed graphs
- Color-coded nodes by function (green for processing, orange for evaluation, blue for action)
- Conditional edges labeled with routing conditions
- Available in both Mermaid and JSON formats via the API

### Real-time Execution Streaming

WebSocket-based live updates during agent execution:

- **Agent stream** (`/ws/agent/{session_id}/`): Node transitions, LLM calls, step completions
- **Dashboard stream** (`/ws/dashboard/`): Live session counts, success rates, active agents
- Implemented with Django Channels and Redis channel layer

### Observability & Tracing

| Tool | Purpose | Configuration |
|------|---------|--------------|
| **LangSmith** | Full LLM execution tracing with prompt/response logging | Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` |
| **Langfuse** | Production monitoring, cost tracking, latency metrics | Set `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` |
| **Flower** | Celery task queue monitoring (success/failure rates, worker status) | Available at port 5557 |
| **Django Admin** | Database inspection, session management | Available at `/admin/` |

---

## Testing

The project uses pytest with Django and asyncio support:

```bash
# Run tests inside the backend container
docker compose exec backend pytest

# Run with verbose output
docker compose exec backend pytest -v

# Run specific test module
docker compose exec backend pytest agents/tests/ -v

# Run with coverage
docker compose exec backend pytest --cov=agents --cov=documents --cov=analytics
```

**Test dependencies:**
- `pytest` 8.0+
- `pytest-django` 4.8+
- `pytest-asyncio` 0.23+
- `factory-boy` 3.3+

---

## Environment Variables

Complete reference of all environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| **Django** | | |
| `DJANGO_SECRET_KEY` | `dev-insecure-key...` | Django secret key (change in production) |
| `DJANGO_DEBUG` | `1` | Debug mode toggle |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:3081,...` | CORS allowed origins |
| **Database** | | |
| `POSTGRES_DB` | `react_rigid_db` | Database name |
| `POSTGRES_USER` | `appuser` | Database user |
| `POSTGRES_PASSWORD` | `changeme_db_password` | Database password |
| `POSTGRES_HOST` | `postgres` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| **Redis** | | |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| **OpenAI** | | |
| `OPENAI_API_KEY` | *(empty)* | **Required** - OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model name |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API base URL |
| **LangSmith** | | |
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | *(empty)* | LangSmith API key |
| `LANGCHAIN_PROJECT` | `react-vs-rigid-qa-app` | LangSmith project name |
| **Langfuse** | | |
| `LANGFUSE_PUBLIC_KEY` | *(empty)* | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | *(empty)* | Langfuse secret key |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse host URL |
| **Celery** | | |
| `CELERY_BROKER_URL` | `redis://redis:6379/1` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/2` | Celery result backend |
| **Ports** | | |
| `FRONTEND_PORT` | `3081` | Frontend external port |
| `BACKEND_PORT` | `8042` | Backend external port |
| `POSTGRES_EXTERNAL_PORT` | `5437` | PostgreSQL external port |
| `REDIS_EXTERNAL_PORT` | `6383` | Redis external port |
| `FLOWER_PORT` | `5557` | Flower external port |
| **Features** | | |
| `MCP_ENABLED` | `true` | Enable MCP tool server |
| `A2A_ENABLED` | `true` | Enable A2A protocol |

---

## Port Configuration

All ports use non-default values to avoid conflicts in multi-service environments:

| Service | External Port | Internal Port | Standard Port |
|---------|---------------|---------------|---------------|
| Frontend (Nginx) | 3081 | 80 | 80 / 3000 |
| Backend (Daphne) | 8042 | 8000 | 8000 |
| PostgreSQL | 5437 | 5432 | 5432 |
| Redis | 6383 | 6379 | 6379 |
| Flower | 5557 | 5555 | 5555 |

---

## Troubleshooting

**Backend returns 500 errors:**
- Check if `OPENAI_API_KEY` is set in `.env`
- Verify with: `docker compose logs backend | tail -50`

**Frontend shows "Network Error":**
- Ensure backend is running: `docker compose ps`
- Check CORS origins include your browser's URL in `.env`

**Agent execution hangs:**
- Check Celery worker: `docker compose logs celery_worker`
- Verify Redis connectivity: `docker compose exec redis redis-cli ping`

**Database connection errors:**
- Wait for PostgreSQL health check: `docker compose ps` (should show "healthy")
- Reset: `docker compose down -v && docker compose up --build -d`

**WebSocket disconnects:**
- Ensure Daphne (ASGI) is running, not Gunicorn (WSGI)
- Check Redis channel layer: `docker compose logs redis`

**Graphs page shows "Graph not available":**
- The backend needs to restart to pick up URL changes: `docker compose restart backend`
- Frontend needs rebuild: `docker compose up --build frontend`

---

## License

This project is provided for educational and research purposes.
