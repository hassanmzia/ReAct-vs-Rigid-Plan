"""
Graph Visualization Service.

Generates Mermaid diagrams and JSON graph definitions
for all agent types.
"""

from .react_agent import ReactAgentService
from .rigid_agent import RigidAgentService
from .multi_agent import MultiAgentOrchestrator
from .recursive_qa import RecursiveQAService


class GraphVisualizer:
    """Generate visual representations of agent graphs."""

    AGENT_SERVICES = {
        "react": ReactAgentService,
        "rigid": RigidAgentService,
        "multi": MultiAgentOrchestrator,
        "recursive": RecursiveQAService,
    }

    @classmethod
    def get_mermaid(cls, agent_type: str) -> str:
        service_cls = cls.AGENT_SERVICES.get(agent_type)
        if not service_cls:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return service_cls().get_mermaid_definition()

    @classmethod
    def get_all_mermaid(cls) -> dict:
        return {
            agent_type: cls.get_mermaid(agent_type)
            for agent_type in cls.AGENT_SERVICES
        }

    @classmethod
    def get_graph_json(cls, agent_type: str) -> dict:
        """Return JSON representation of the graph structure."""
        graphs = {
            "react": {
                "nodes": [
                    {"id": "start", "label": "Start", "type": "start"},
                    {"id": "react_node", "label": "React Node", "type": "process",
                     "description": "Contact lookup with adaptive reasoning"},
                    {"id": "contact_node", "label": "Contact Node", "type": "process",
                     "description": "LLM-based disambiguation"},
                    {"id": "email_node", "label": "Email Node", "type": "process",
                     "description": "LLM email generation"},
                    {"id": "end", "label": "End", "type": "end"},
                ],
                "edges": [
                    {"from": "start", "to": "react_node", "label": ""},
                    {"from": "react_node", "to": "email_node", "label": "approve",
                     "condition": True},
                    {"from": "react_node", "to": "contact_node", "label": "fail",
                     "condition": True},
                    {"from": "react_node", "to": "end", "label": "END",
                     "condition": True},
                    {"from": "contact_node", "to": "react_node", "label": "retry"},
                    {"from": "email_node", "to": "end", "label": ""},
                ],
            },
            "rigid": {
                "nodes": [
                    {"id": "start", "label": "Start", "type": "start"},
                    {"id": "planner", "label": "Planner", "type": "process",
                     "description": "Fixed plan generation"},
                    {"id": "contacts", "label": "Contacts", "type": "process",
                     "description": "Database lookup"},
                    {"id": "email", "label": "Email", "type": "process",
                     "description": "Send email"},
                    {"id": "end", "label": "End", "type": "end"},
                ],
                "edges": [
                    {"from": "start", "to": "planner", "label": ""},
                    {"from": "planner", "to": "contacts", "label": ""},
                    {"from": "contacts", "to": "email", "label": ""},
                    {"from": "email", "to": "end", "label": ""},
                ],
            },
            "multi": {
                "nodes": [
                    {"id": "start", "label": "Start", "type": "start"},
                    {"id": "supervisor", "label": "Supervisor", "type": "process",
                     "description": "Workflow orchestrator"},
                    {"id": "research", "label": "Research Agent", "type": "agent",
                     "description": "Information gathering"},
                    {"id": "reasoning", "label": "Reasoning Agent", "type": "agent",
                     "description": "Analysis & synthesis"},
                    {"id": "action", "label": "Action Agent", "type": "agent",
                     "description": "Task execution"},
                    {"id": "synthesize", "label": "Synthesizer", "type": "process",
                     "description": "Final output"},
                    {"id": "end", "label": "End", "type": "end"},
                ],
                "edges": [
                    {"from": "start", "to": "supervisor", "label": ""},
                    {"from": "supervisor", "to": "research", "label": "research",
                     "condition": True},
                    {"from": "supervisor", "to": "reasoning", "label": "reasoning",
                     "condition": True},
                    {"from": "supervisor", "to": "action", "label": "action",
                     "condition": True},
                    {"from": "supervisor", "to": "synthesize", "label": "synthesize",
                     "condition": True},
                    {"from": "research", "to": "supervisor", "label": ""},
                    {"from": "reasoning", "to": "supervisor", "label": ""},
                    {"from": "action", "to": "supervisor", "label": ""},
                    {"from": "synthesize", "to": "end", "label": ""},
                ],
            },
            "recursive": {
                "nodes": [
                    {"id": "start", "label": "Start", "type": "start"},
                    {"id": "answer", "label": "Answer Node", "type": "process",
                     "description": "Generate answer"},
                    {"id": "evaluate", "label": "Evaluate Node", "type": "process",
                     "description": "Quality assessment"},
                    {"id": "refine", "label": "Refine Node", "type": "process",
                     "description": "Query optimization"},
                    {"id": "end", "label": "End", "type": "end"},
                ],
                "edges": [
                    {"from": "start", "to": "answer", "label": ""},
                    {"from": "answer", "to": "evaluate", "label": ""},
                    {"from": "evaluate", "to": "refine", "label": "refine",
                     "condition": True},
                    {"from": "evaluate", "to": "end", "label": "end",
                     "condition": True},
                    {"from": "refine", "to": "answer", "label": ""},
                ],
            },
        }
        if agent_type not in graphs:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return graphs[agent_type]
