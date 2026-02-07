"""
Agent-to-Agent (A2A) Communication Service.

Implements the A2A protocol for inter-agent communication:
- Agent Card discovery
- Task delegation and routing
- Message passing between agents
- Capability negotiation
"""

import logging
import uuid
from typing import Optional
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class AgentCard:
    """A2A Agent Card - describes agent capabilities."""

    def __init__(self, agent_id: str, name: str, description: str,
                 capabilities: list[str], url: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.url = url

    def to_dict(self) -> dict:
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "url": self.url,
            "protocol": "a2a/1.0",
        }


class A2AMessage:
    """A2A protocol message."""

    def __init__(self, sender: str, receiver: str, task_type: str,
                 payload: dict, correlation_id: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.task_type = task_type
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.status = "pending"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "task_type": self.task_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "status": self.status,
        }


class A2AService:
    """Manages Agent-to-Agent communication."""

    def __init__(self):
        self.agents: dict[str, AgentCard] = {}
        self.message_log: list[dict] = []
        self._register_default_agents()

    def _register_default_agents(self):
        self.register_agent(AgentCard(
            agent_id="react-agent",
            name="Adaptive ReAct Agent",
            description="Handles ambiguous tasks using LLM-based reasoning loops",
            capabilities=["contact_lookup", "email_send", "disambiguation"],
            url="/api/agents/sessions/run-sync/",
        ))
        self.register_agent(AgentCard(
            agent_id="rigid-agent",
            name="Rigid Plan-and-Execute Agent",
            description="Executes fixed workflow plans sequentially",
            capabilities=["contact_lookup", "email_send"],
            url="/api/agents/sessions/run-sync/",
        ))
        self.register_agent(AgentCard(
            agent_id="multi-agent",
            name="Multi-Agent Orchestrator",
            description="Coordinates research, reasoning, and action agents",
            capabilities=["research", "reasoning", "action", "synthesis"],
            url="/api/agents/sessions/run-sync/",
        ))
        self.register_agent(AgentCard(
            agent_id="recursive-qa",
            name="Recursive Q&A Agent",
            description="Iteratively refines queries for high-confidence answers",
            capabilities=["qa", "refinement", "confidence_scoring"],
            url="/api/agents/sessions/recursive-qa-sync/",
        ))
        self.register_agent(AgentCard(
            agent_id="document-agent",
            name="Document Processing Agent",
            description="Processes and indexes PDF documents for RAG",
            capabilities=["pdf_processing", "text_extraction", "indexing"],
            url="/api/documents/",
        ))

    def register_agent(self, card: AgentCard):
        self.agents[card.agent_id] = card
        logger.info(f"A2A: Registered agent '{card.name}' ({card.agent_id})")

    def discover_agents(self, capability: Optional[str] = None) -> list[dict]:
        if capability:
            return [
                card.to_dict() for card in self.agents.values()
                if capability in card.capabilities
            ]
        return [card.to_dict() for card in self.agents.values()]

    def send_message(self, sender: str, receiver: str, task_type: str,
                     payload: dict) -> A2AMessage:
        if receiver not in self.agents:
            raise ValueError(f"Unknown agent: {receiver}")

        msg = A2AMessage(sender, receiver, task_type, payload)
        self.message_log.append(msg.to_dict())
        logger.info(f"A2A: Message {msg.id} from {sender} -> {receiver}")
        return msg

    def get_message_log(self, limit: int = 50) -> list[dict]:
        return self.message_log[-limit:]

    def delegate_task(self, task_type: str, payload: dict) -> dict:
        """Find the best agent for a task and delegate."""
        for card in self.agents.values():
            if task_type in card.capabilities:
                msg = self.send_message("supervisor", card.agent_id, task_type, payload)
                return {
                    "delegated_to": card.agent_id,
                    "message_id": msg.id,
                    "agent_url": card.url,
                }
        return {"error": f"No agent found for capability: {task_type}"}


# Singleton
a2a_service = A2AService()
