export type AgentType = 'react' | 'rigid' | 'multi' | 'recursive';
export type SessionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Contact {
  id: number;
  name: string;
  email: string;
  department: string;
  role: string;
  phone: string;
  is_active: boolean;
}

export interface AgentStep {
  id: string;
  node_name: string;
  step_number: number;
  status: string;
  input_state: Record<string, unknown>;
  output_state: Record<string, unknown>;
  log_messages: LogEntry[];
  duration_ms: number | null;
  created_at: string;
}

export interface LogEntry {
  level: string;
  time: string;
  message: string;
}

export interface QueryHistoryEntry {
  id: string;
  iteration: number;
  original_query: string;
  refined_query: string;
  answer: string;
  confidence_score: number | null;
  is_final: boolean;
  created_at: string;
}

export interface AgentSession {
  id: string;
  agent_type: AgentType;
  status: SessionStatus;
  user_message: string;
  user_name_target: string;
  final_result: Record<string, unknown> | null;
  error_message: string;
  execution_time_ms: number | null;
  retry_count: number;
  graph_definition: { mermaid?: string } | null;
  langsmith_run_id: string;
  langfuse_trace_id: string;
  steps: AgentStep[];
  query_history: QueryHistoryEntry[];
  created_at: string;
  updated_at: string;
  steps_count?: number;
  iterations_count?: number;
}

export interface AgentComparison {
  id: string;
  query: string;
  react_session: AgentSession;
  rigid_session: AgentSession;
  winner: string;
  analysis: string;
  created_at: string;
}

export interface Document {
  id: string;
  title: string;
  file: string;
  doc_type: string;
  file_size: number;
  page_count: number | null;
  processing_status: string;
  chunk_count: number;
  created_at: string;
}

export interface DashboardStats {
  overview: {
    total_sessions: number;
    recent_sessions_24h: number;
    success_rate: number;
    total_documents: number;
    processed_documents: number;
  };
  by_agent_type: Array<{
    agent_type: string;
    count: number;
    avg_time: number | null;
  }>;
  by_status: Array<{
    status: string;
    count: number;
  }>;
  comparisons: {
    total: number;
    react_wins: number;
    rigid_wins: number;
    tie_or_none: number;
  };
  recursive_qa: {
    avg_confidence: number | null;
    total_iterations: number;
  };
}

export interface RunAgentRequest {
  agent_type: AgentType;
  message: string;
  user_name?: string;
  max_iterations?: number;
}

export interface CompareRequest {
  message: string;
  user_name?: string;
}

export interface RecursiveQARequest {
  query: string;
  max_refinements?: number;
  target_confidence?: number;
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    description?: string;
  }>;
  edges: Array<{
    from: string;
    to: string;
    label: string;
    condition?: boolean;
  }>;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface A2AAgent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  url: string;
  protocol: string;
}
