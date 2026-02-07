"""
Adaptive ReAct Agent Service - based on notebook implementation.

Implements the ReAct (Reason + Act) pattern with:
- Conditional routing based on contact lookup results
- LLM-based disambiguation for ambiguous matches
- Retry logic with adaptive reasoning
- Email generation via LLM
"""

import time
import logging
from typing import TypedDict, Optional, Any
from datetime import datetime

from django.conf import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel, Field

from agents.models import Contact

logger = logging.getLogger(__name__)


class RelevantCandidate(BaseModel):
    """Structured output to extract the most relevant contact name."""
    user_name: str = Field(
        description="The most relevant employee name to send a mail to based on user message."
    )


class ReactAgentState(TypedDict):
    flag: Optional[str]
    counter: int
    user_name: Optional[str]
    details: Optional[dict]
    error: Optional[str]
    message: Optional[str]
    email_content: Optional[str]
    logs: list
    step_history: list


class ReactAgentService:
    """Adaptive ReAct agent that handles ambiguity via LLM reasoning loops."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )
        self.structured_model = self.llm.with_structured_output(RelevantCandidate)
        self._graph = None

    def _get_contacts_db(self) -> dict:
        """Load contacts from database."""
        contacts = Contact.objects.filter(is_active=True)
        return {
            c.name: {"email": c.email, "department": c.department, "role": c.role}
            for c in contacts
        }

    def _log(self, level: str, message: str, state: ReactAgentState) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        entry = {"level": level, "time": ts, "message": message}
        state["logs"].append(entry)
        getattr(logger, level.lower(), logger.info)(message)

    MAX_RETRIES = 5

    def _react_node(self, state: ReactAgentState) -> dict:
        """Core ReAct reasoning node - checks contacts and decides routing."""
        counter = state.get("counter", 0)
        if counter >= self.MAX_RETRIES:
            self._log("ERROR", f"react_node: Max retries ({self.MAX_RETRIES}) exceeded, giving up", state)
            state["step_history"].append({
                "node": "react_node",
                "action": "max_retries_exceeded",
                "attempts": counter,
                "timestamp": datetime.now().isoformat(),
            })
            return {
                "error": f"MAX_RETRIES_EXCEEDED after {counter} attempts",
                "flag": "END",
                "logs": state["logs"],
                "step_history": state["step_history"],
            }

        self._log("INFO", f"react_node: Checking contacts for '{state['user_name']}'", state)

        contacts_db = self._get_contacts_db()
        user_name = state["user_name"] or ""
        search_terms = user_name.lower().split()
        matches = [
            name for name in contacts_db
            if all(
                any(term == part for part in name.lower().split())
                for term in search_terms
            )
        ]

        state["step_history"].append({
            "node": "react_node",
            "action": "contact_lookup",
            "input": user_name,
            "matches": matches,
            "timestamp": datetime.now().isoformat(),
        })

        if len(matches) == 1:
            name = matches[0]
            self._log("INFO", f"react_node: Single match found -> {name}", state)
            return {
                "details": {"name": name, **contacts_db[name]},
                "flag": "approve",
                "logs": state["logs"],
                "step_history": state["step_history"],
            }
        elif len(matches) > 1:
            self._log("WARNING", f"react_node: Ambiguity detected -> {matches}", state)
            return {
                "error": f"AMBIGUOUS: {matches}",
                "flag": "fail",
                "logs": state["logs"],
                "step_history": state["step_history"],
            }
        else:
            self._log("ERROR", "react_node: No contact found in DB", state)
            return {
                "error": "CONTACT_NOT_FOUND",
                "flag": "END",
                "logs": state["logs"],
                "step_history": state["step_history"],
            }

    def _contact_node(self, state: ReactAgentState) -> dict:
        """Uses LLM to resolve ambiguity - retry logic with reasoning."""
        counter = state.get("counter", 0) + 1
        self._log("WARNING", f"contact_node: Resolving ambiguity, attempt #{counter}", state)

        contacts_db = self._get_contacts_db()
        prompt = f"""
You are an expert in contextual reasoning and corporate organizational analysis.
Analyze the user request and employee database to identify the single most relevant person.

Principles:
- Prioritize exact or close matches between role/department and the task
- Consider hierarchical level for decision-making tasks
- Use contextual understanding of the message intent
- Only select from the given database
- Output should only contain the name

### USER MESSAGE:
{state['message']}

### EMPLOYEE DATABASE:
{contacts_db}

### RESPONSE:
"""
        result = self.structured_model.invoke(prompt)
        resolved_name = result.user_name
        self._log("INFO", f"contact_node: LLM resolved to -> {resolved_name}", state)

        state["step_history"].append({
            "node": "contact_node",
            "action": "llm_disambiguation",
            "resolved_to": resolved_name,
            "attempt": counter,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "user_name": resolved_name,
            "counter": counter,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _email_node(self, state: ReactAgentState) -> dict:
        """Generates and 'sends' email using LLM."""
        email_addr = state["details"].get("email", "unknown")
        self._log("INFO", f"email_node: Generating email to {email_addr}", state)

        prompt = f"""Write a professional email to {state['details'].get('email')}.
The topic of the email is: {state['message']}.
Maintain a formal tone. Provide a clear subject line and closing.

**To:** <Email of the recipient>
**Subject:** <Subject of the email>
**Body:** <Body of the email and closing>
"""
        email_content = self.llm.invoke(prompt).content

        state["step_history"].append({
            "node": "email_node",
            "action": "email_generated",
            "to": email_addr,
            "timestamp": datetime.now().isoformat(),
        })

        self._log("INFO", "email_node: Email generated successfully", state)
        return {
            "email_content": email_content,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def build_graph(self) -> StateGraph:
        """Build the ReAct agent LangGraph."""
        workflow = StateGraph(ReactAgentState)

        workflow.add_node("react_node", self._react_node)
        workflow.add_node("contact_node", self._contact_node)
        workflow.add_node("email_node", self._email_node)

        workflow.add_edge(START, "react_node")
        workflow.add_conditional_edges(
            "react_node",
            lambda state: state["flag"],
            {
                "approve": "email_node",
                "fail": "contact_node",
                "END": END,
            },
        )
        workflow.add_edge("contact_node", "react_node")
        workflow.add_edge("email_node", END)

        return workflow

    def get_compiled_graph(self):
        if self._graph is None:
            self._graph = self.build_graph().compile(recursion_limit=25)
        return self._graph

    def run(self, message: str, user_name: str = "") -> dict:
        """Execute the ReAct agent."""
        start = time.time()
        graph = self.get_compiled_graph()

        initial_state: ReactAgentState = {
            "flag": None,
            "counter": 0,
            "user_name": user_name,
            "details": None,
            "error": None,
            "message": message,
            "email_content": None,
            "logs": [],
            "step_history": [],
        }

        output = graph.invoke(initial_state)
        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "status": "completed" if output.get("email_content") else "failed",
            "result": {
                "email_content": output.get("email_content"),
                "contact": output.get("details"),
                "error": output.get("error"),
            },
            "logs": output.get("logs", []),
            "step_history": output.get("step_history", []),
            "execution_time_ms": elapsed_ms,
            "retry_count": output.get("counter", 0),
        }

    def get_mermaid_definition(self) -> str:
        """Return Mermaid diagram definition for this agent's graph."""
        return """graph TD
    START((Start)) --> react_node[React Node<br/>Contact Lookup & Reasoning]
    react_node -->|approve| email_node[Email Node<br/>LLM Email Generation]
    react_node -->|fail| contact_node[Contact Node<br/>LLM Disambiguation]
    react_node -->|END| END_NODE((End))
    contact_node --> react_node
    email_node --> END_NODE

    style react_node fill:#4CAF50,color:#fff
    style contact_node fill:#FF9800,color:#fff
    style email_node fill:#2196F3,color:#fff
    style START fill:#9C27B0,color:#fff
    style END_NODE fill:#f44336,color:#fff"""
