"""
Rigid Plan-and-Execute Agent Service - based on notebook implementation.

Implements the fixed Plan-and-Execute pattern with:
- Predetermined step sequence (plan -> contacts -> email)
- No adaptive routing or retry logic
- Fails on ambiguous contact matches
"""

import time
import logging
from typing import TypedDict, Optional, Any, List
from datetime import datetime

from django.conf import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START

from agents.models import Contact

logger = logging.getLogger(__name__)


class RigidAgentState(TypedDict):
    user: str
    steps: List[Any]
    contact: Optional[str]
    contact_result: dict
    email_result: Optional[str]
    logs: list
    step_history: list


class RigidAgentService:
    """Rigid Plan-and-Execute agent with fixed workflow."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )
        self._graph = None

    def _get_contacts_db(self) -> dict:
        contacts = Contact.objects.filter(is_active=True)
        return {
            c.name: {"email": c.email, "department": c.department, "role": c.role}
            for c in contacts
        }

    def _log(self, level: str, message: str, state: RigidAgentState) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {"level": level, "time": ts, "message": message}
        state["logs"].append(entry)
        getattr(logger, level.lower(), logger.info)(message)

    def _plan_node(self, state: RigidAgentState) -> dict:
        """Create a fixed execution plan."""
        self._log("INFO", f"plan_node: Planning for user '{state['user']}'", state)

        plan = {
            "steps": [
                ("contacts", state["user"]),
                ("email_send", state["user"]),
            ]
        }

        state["step_history"].append({
            "node": "plan_node",
            "action": "plan_created",
            "steps": [str(s) for s in plan["steps"]],
            "timestamp": datetime.now().isoformat(),
        })

        self._log("INFO", f"plan_node: Plan -> {plan['steps']}", state)
        return {
            "steps": plan["steps"],
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _contacts_node(self, state: RigidAgentState) -> dict:
        """Look up contact - no retry logic."""
        step_action, step_arg = state["steps"][0]
        self._log("INFO", f"contacts_node: Looking up '{step_arg}'", state)

        contacts_db = self._get_contacts_db()
        matches = [name for name in contacts_db if step_arg.lower() in name.lower()]

        if len(matches) == 1:
            name = matches[0]
            result = {"success": True, "contact": {"name": name, **contacts_db[name]}}
            self._log("INFO", f"contacts_node: Found -> {name}", state)
        elif len(matches) > 1:
            result = {"success": False, "error": f"AMBIGUOUS: {matches}"}
            self._log("WARNING", f"contacts_node: Ambiguous -> {matches}", state)
        else:
            result = {"success": False, "error": "CONTACT_NOT_FOUND"}
            self._log("ERROR", "contacts_node: Not found", state)

        state["step_history"].append({
            "node": "contacts_node",
            "action": "contact_lookup",
            "input": step_arg,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "contact_result": result,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _email_node(self, state: RigidAgentState) -> dict:
        """Send email - fails if contact lookup failed."""
        result = state["contact_result"]
        self._log("INFO", f"email_node: Previous result -> {result}", state)

        if not result.get("success"):
            error_msg = f"Cannot send email: {result.get('error')}"
            self._log("ERROR", f"email_node: {error_msg}", state)
            state["step_history"].append({
                "node": "email_node",
                "action": "email_failed",
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
            })
            return {
                "email_result": error_msg,
                "logs": state["logs"],
                "step_history": state["step_history"],
            }

        contact = result["contact"]
        subject = "Budget Meeting"
        body = f"""Hi {contact['name']},

I hope you're doing well. We need to discuss the budget for the upcoming project.
Please let me know when you're available for a quick call or meeting.

Best regards"""

        email_result = f"Email sent to {contact['name']} ({contact['email']}) | subject='{subject}'"
        self._log("INFO", f"email_node: {email_result}", state)

        state["step_history"].append({
            "node": "email_node",
            "action": "email_sent",
            "to": contact["email"],
            "subject": subject,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "email_result": email_result,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def build_graph(self) -> StateGraph:
        """Build the Rigid agent LangGraph."""
        workflow = StateGraph(RigidAgentState)

        workflow.add_node("planner", self._plan_node)
        workflow.add_node("contacts", self._contacts_node)
        workflow.add_node("email", self._email_node)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "contacts")
        workflow.add_edge("contacts", "email")
        workflow.set_finish_point("email")

        return workflow

    def get_compiled_graph(self):
        if self._graph is None:
            self._graph = self.build_graph().compile()
        return self._graph

    def run(self, message: str, user_name: str = "") -> dict:
        """Execute the Rigid agent."""
        start = time.time()
        graph = self.get_compiled_graph()

        initial_state: RigidAgentState = {
            "user": user_name or message,
            "steps": [],
            "contact": None,
            "contact_result": {},
            "email_result": None,
            "logs": [],
            "step_history": [],
        }

        output = graph.invoke(initial_state)
        elapsed_ms = int((time.time() - start) * 1000)

        email_result = output.get("email_result", "")
        is_success = email_result and "Email sent" in email_result

        return {
            "status": "completed" if is_success else "failed",
            "result": {
                "email_result": email_result,
                "contact": output.get("contact_result", {}).get("contact"),
                "error": None if is_success else email_result,
            },
            "logs": output.get("logs", []),
            "step_history": output.get("step_history", []),
            "execution_time_ms": elapsed_ms,
            "retry_count": 0,
        }

    def get_mermaid_definition(self) -> str:
        return """graph TD
    START((Start)) --> planner[Planner<br/>Fixed Plan Generation]
    planner --> contacts[Contacts<br/>Database Lookup]
    contacts --> email[Email<br/>Send Email]
    email --> END_NODE((End))

    style planner fill:#9C27B0,color:#fff
    style contacts fill:#4CAF50,color:#fff
    style email fill:#2196F3,color:#fff
    style START fill:#607D8B,color:#fff
    style END_NODE fill:#f44336,color:#fff"""
