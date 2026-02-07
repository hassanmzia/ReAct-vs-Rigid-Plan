"""
Model Context Protocol (MCP) Service.

Provides a tool server that exposes agent capabilities
as MCP-compatible tools for external consumption.
"""

import logging
from typing import Any
from django.conf import settings

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry of MCP-compatible tools exposed by this application."""

    def __init__(self):
        self.tools: dict[str, dict] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(
            name="contact_lookup",
            description="Look up a contact in the corporate database by name",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Contact name to search for"},
                },
                "required": ["name"],
            },
            handler=self._handle_contact_lookup,
        )
        self.register_tool(
            name="run_react_agent",
            description="Execute an Adaptive ReAct agent for a given task",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Task description"},
                    "user_name": {"type": "string", "description": "Target contact name"},
                },
                "required": ["message"],
            },
            handler=self._handle_run_react,
        )
        self.register_tool(
            name="run_rigid_agent",
            description="Execute a Rigid Plan-and-Execute agent for a given task",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Task description"},
                    "user_name": {"type": "string", "description": "Target contact name"},
                },
                "required": ["message"],
            },
            handler=self._handle_run_rigid,
        )
        self.register_tool(
            name="recursive_qa",
            description="Run recursive Q&A with iterative refinement",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Question to answer"},
                    "max_refinements": {"type": "integer", "default": 3},
                    "target_confidence": {"type": "number", "default": 0.85},
                },
                "required": ["query"],
            },
            handler=self._handle_recursive_qa,
        )
        self.register_tool(
            name="compare_agents",
            description="Compare ReAct vs Rigid agent execution on the same task",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Task to compare"},
                    "user_name": {"type": "string", "description": "Target contact"},
                },
                "required": ["message"],
            },
            handler=self._handle_compare,
        )

    def register_tool(self, name: str, description: str, parameters: dict, handler):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": parameters,
            "handler": handler,
        }

    def list_tools(self) -> list[dict]:
        return [
            {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
            for t in self.tools.values()
        ]

    def call_tool(self, name: str, arguments: dict) -> dict:
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        try:
            return self.tools[name]["handler"](arguments)
        except Exception as e:
            logger.exception(f"MCP tool '{name}' failed")
            return {"error": str(e)}

    def _handle_contact_lookup(self, args: dict) -> dict:
        from agents.models import Contact
        name = args.get("name", "")
        contacts = Contact.objects.filter(name__icontains=name, is_active=True)
        return {
            "results": [
                {"name": c.name, "email": c.email, "department": c.department}
                for c in contacts
            ]
        }

    def _handle_run_react(self, args: dict) -> dict:
        from agents.services.react_agent import ReactAgentService
        service = ReactAgentService()
        return service.run(args["message"], args.get("user_name", ""))

    def _handle_run_rigid(self, args: dict) -> dict:
        from agents.services.rigid_agent import RigidAgentService
        service = RigidAgentService()
        return service.run(args["message"], args.get("user_name", ""))

    def _handle_recursive_qa(self, args: dict) -> dict:
        from agents.services.recursive_qa import RecursiveQAService
        service = RecursiveQAService()
        return service.run(
            args["query"],
            max_refinements=args.get("max_refinements", 3),
            target_confidence=args.get("target_confidence", 0.85),
        )

    def _handle_compare(self, args: dict) -> dict:
        from agents.tasks import _execute_comparison
        comparison = _execute_comparison(args["message"], args.get("user_name", ""))
        return {
            "winner": comparison.winner,
            "analysis": comparison.analysis,
            "react_session_id": str(comparison.react_session_id),
            "rigid_session_id": str(comparison.rigid_session_id),
        }


# Singleton
mcp_registry = MCPToolRegistry()
