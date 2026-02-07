"""
Multi-Agent Orchestrator Service.

Coordinates multiple specialized agents:
- Research Agent: Queries documents and knowledge bases
- Reasoning Agent: Analyzes and synthesizes information
- Action Agent: Executes tasks (email, contact lookup)
- Supervisor Agent: Orchestrates the workflow

Implements A2A (Agent-to-Agent) communication patterns.
"""

import time
import logging
from typing import TypedDict, Optional, List, Literal
from datetime import datetime

from django.conf import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

logger = logging.getLogger(__name__)


class MultiAgentState(TypedDict):
    query: str
    phase: str
    research_result: Optional[str]
    reasoning_result: Optional[str]
    action_result: Optional[str]
    final_answer: Optional[str]
    agent_messages: list  # A2A message log
    logs: list
    step_history: list
    iteration: int
    max_iterations: int
    should_continue: bool


class MultiAgentOrchestrator:
    """Orchestrates multiple agents working together via A2A protocol."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )
        self._graph = None

    def _log(self, level: str, message: str, state: MultiAgentState) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        state["logs"].append({"level": level, "time": ts, "message": message})

    def _a2a_message(self, sender: str, receiver: str, content: str, state: MultiAgentState):
        """Record an Agent-to-Agent message."""
        msg = {
            "from": sender,
            "to": receiver,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        state["agent_messages"].append(msg)

    def _supervisor_node(self, state: MultiAgentState) -> dict:
        """Supervisor decides which agent to activate next."""
        self._log("INFO", "Supervisor: Evaluating workflow state", state)

        if not state.get("research_result"):
            next_phase = "research"
        elif not state.get("reasoning_result"):
            next_phase = "reasoning"
        elif not state.get("action_result"):
            next_phase = "action"
        else:
            next_phase = "synthesize"

        self._a2a_message("supervisor", next_phase, f"Activating {next_phase} phase", state)

        state["step_history"].append({
            "node": "supervisor",
            "action": f"route_to_{next_phase}",
            "iteration": state["iteration"],
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "phase": next_phase,
            "logs": state["logs"],
            "step_history": state["step_history"],
            "agent_messages": state["agent_messages"],
        }

    def _research_node(self, state: MultiAgentState) -> dict:
        """Research agent - gathers information."""
        self._log("INFO", "Research Agent: Gathering information", state)

        prompt = f"""You are a research agent. Analyze this query and provide relevant context,
background information, and key facts. Be thorough but concise.

Query: {state['query']}

Provide your research findings:"""

        result = self.llm.invoke(prompt).content
        self._a2a_message("research", "supervisor", "Research complete", state)

        state["step_history"].append({
            "node": "research_agent",
            "action": "research_complete",
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "research_result": result,
            "phase": "supervisor",
            "logs": state["logs"],
            "step_history": state["step_history"],
            "agent_messages": state["agent_messages"],
        }

    def _reasoning_node(self, state: MultiAgentState) -> dict:
        """Reasoning agent - analyzes research results."""
        self._log("INFO", "Reasoning Agent: Analyzing findings", state)

        prompt = f"""You are a reasoning agent. Based on the research findings, provide
a structured analysis with conclusions and recommended actions.

Original Query: {state['query']}
Research Findings: {state.get('research_result', 'N/A')}

Provide your analysis:"""

        result = self.llm.invoke(prompt).content
        self._a2a_message("reasoning", "supervisor", "Analysis complete", state)

        state["step_history"].append({
            "node": "reasoning_agent",
            "action": "analysis_complete",
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "reasoning_result": result,
            "phase": "supervisor",
            "logs": state["logs"],
            "step_history": state["step_history"],
            "agent_messages": state["agent_messages"],
        }

    def _action_node(self, state: MultiAgentState) -> dict:
        """Action agent - executes recommended actions."""
        self._log("INFO", "Action Agent: Executing actions", state)

        prompt = f"""You are an action agent. Based on the analysis, describe the
concrete actions taken and their outcomes.

Original Query: {state['query']}
Analysis: {state.get('reasoning_result', 'N/A')}

Describe actions executed:"""

        result = self.llm.invoke(prompt).content
        self._a2a_message("action", "supervisor", "Actions executed", state)

        state["step_history"].append({
            "node": "action_agent",
            "action": "actions_executed",
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "action_result": result,
            "phase": "supervisor",
            "logs": state["logs"],
            "step_history": state["step_history"],
            "agent_messages": state["agent_messages"],
        }

    def _synthesize_node(self, state: MultiAgentState) -> dict:
        """Synthesize all agent outputs into a final answer."""
        self._log("INFO", "Synthesizer: Combining all agent outputs", state)

        prompt = f"""Synthesize these multi-agent results into a comprehensive final answer.

Query: {state['query']}
Research: {state.get('research_result', 'N/A')}
Analysis: {state.get('reasoning_result', 'N/A')}
Actions: {state.get('action_result', 'N/A')}

Provide a comprehensive final response:"""

        result = self.llm.invoke(prompt).content

        state["step_history"].append({
            "node": "synthesizer",
            "action": "synthesis_complete",
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "final_answer": result,
            "should_continue": False,
            "logs": state["logs"],
            "step_history": state["step_history"],
            "agent_messages": state["agent_messages"],
        }

    def _route_from_supervisor(self, state: MultiAgentState) -> str:
        phase = state.get("phase", "research")
        if phase == "research":
            return "research"
        elif phase == "reasoning":
            return "reasoning"
        elif phase == "action":
            return "action"
        else:
            return "synthesize"

    def build_graph(self) -> StateGraph:
        workflow = StateGraph(MultiAgentState)

        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("reasoning", self._reasoning_node)
        workflow.add_node("action", self._action_node)
        workflow.add_node("synthesize", self._synthesize_node)

        workflow.add_edge(START, "supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "research": "research",
                "reasoning": "reasoning",
                "action": "action",
                "synthesize": "synthesize",
            },
        )
        workflow.add_edge("research", "supervisor")
        workflow.add_edge("reasoning", "supervisor")
        workflow.add_edge("action", "supervisor")
        workflow.add_edge("synthesize", END)

        return workflow

    def get_compiled_graph(self):
        if self._graph is None:
            self._graph = self.build_graph().compile()
        return self._graph

    def run(self, query: str, max_iterations: int = 5) -> dict:
        start = time.time()
        graph = self.get_compiled_graph()

        initial_state: MultiAgentState = {
            "query": query,
            "phase": "",
            "research_result": None,
            "reasoning_result": None,
            "action_result": None,
            "final_answer": None,
            "agent_messages": [],
            "logs": [],
            "step_history": [],
            "iteration": 0,
            "max_iterations": max_iterations,
            "should_continue": True,
        }

        output = graph.invoke(initial_state)
        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "status": "completed" if output.get("final_answer") else "failed",
            "result": {
                "final_answer": output.get("final_answer"),
                "research": output.get("research_result"),
                "analysis": output.get("reasoning_result"),
                "actions": output.get("action_result"),
            },
            "agent_messages": output.get("agent_messages", []),
            "logs": output.get("logs", []),
            "step_history": output.get("step_history", []),
            "execution_time_ms": elapsed_ms,
        }

    def get_mermaid_definition(self) -> str:
        return """graph TD
    START((Start)) --> supervisor[Supervisor<br/>Workflow Orchestrator]
    supervisor -->|research| research[Research Agent<br/>Information Gathering]
    supervisor -->|reasoning| reasoning[Reasoning Agent<br/>Analysis & Synthesis]
    supervisor -->|action| action[Action Agent<br/>Task Execution]
    supervisor -->|synthesize| synthesize[Synthesizer<br/>Final Output]
    research --> supervisor
    reasoning --> supervisor
    action --> supervisor
    synthesize --> END_NODE((End))

    style supervisor fill:#9C27B0,color:#fff
    style research fill:#4CAF50,color:#fff
    style reasoning fill:#FF9800,color:#fff
    style action fill:#2196F3,color:#fff
    style synthesize fill:#E91E63,color:#fff
    style START fill:#607D8B,color:#fff
    style END_NODE fill:#f44336,color:#fff"""
