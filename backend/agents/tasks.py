"""Celery tasks for async agent execution."""

import logging
import time
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def _send_ws_update(session_id: str, data: dict):
    """Send WebSocket update to connected clients."""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"agent_{session_id}",
            {"type": "agent.update", "data": data},
        )
    except Exception as e:
        logger.warning(f"WebSocket send failed: {e}")


def _execute_agent(session_id: str):
    """Core agent execution logic."""
    from agents.models import AgentSession, AgentStep
    from agents.services.react_agent import ReactAgentService
    from agents.services.rigid_agent import RigidAgentService
    from agents.services.multi_agent import MultiAgentOrchestrator

    session = AgentSession.objects.get(id=session_id)
    session.status = AgentSession.Status.RUNNING
    session.save(update_fields=["status"])

    _send_ws_update(session_id, {"status": "running", "agent_type": session.agent_type})

    try:
        if session.agent_type == AgentSession.AgentType.REACT:
            service = ReactAgentService()
            result = service.run(session.user_message, session.user_name_target)
            session.graph_definition = {"mermaid": service.get_mermaid_definition()}
        elif session.agent_type == AgentSession.AgentType.RIGID:
            service = RigidAgentService()
            result = service.run(session.user_message, session.user_name_target)
            session.graph_definition = {"mermaid": service.get_mermaid_definition()}
        elif session.agent_type == AgentSession.AgentType.MULTI:
            service = MultiAgentOrchestrator()
            result = service.run(session.user_message)
            session.graph_definition = {"mermaid": service.get_mermaid_definition()}
        else:
            raise ValueError(f"Unsupported agent type: {session.agent_type}")

        session.status = (
            AgentSession.Status.COMPLETED
            if result["status"] == "completed"
            else AgentSession.Status.FAILED
        )
        session.final_result = result.get("result")
        session.execution_time_ms = result.get("execution_time_ms")
        session.retry_count = result.get("retry_count", 0)

        if result.get("error"):
            session.error_message = str(result["error"])

        # Save step history
        for i, step in enumerate(result.get("step_history", [])):
            AgentStep.objects.create(
                session=session,
                node_name=step.get("node", "unknown"),
                step_number=i + 1,
                status=AgentStep.StepStatus.COMPLETED,
                input_state={"action": step.get("action")},
                output_state=step,
                log_messages=[],
                duration_ms=0,
            )

        session.save()
        _send_ws_update(session_id, {
            "status": session.status,
            "result": result.get("result"),
            "execution_time_ms": result.get("execution_time_ms"),
        })

    except Exception as e:
        logger.exception(f"Agent execution failed: {e}")
        session.status = AgentSession.Status.FAILED
        session.error_message = str(e)
        session.save()
        _send_ws_update(session_id, {"status": "failed", "error": str(e)})


def _execute_comparison(message: str, user_name: str = ""):
    """Execute both agents and compare."""
    from agents.models import AgentSession, AgentComparison
    from agents.services.react_agent import ReactAgentService
    from agents.services.rigid_agent import RigidAgentService

    # Run ReAct
    react_session = AgentSession.objects.create(
        agent_type=AgentSession.AgentType.REACT,
        status=AgentSession.Status.PENDING,
        user_message=message,
        user_name_target=user_name,
    )
    _execute_agent(str(react_session.id))
    react_session.refresh_from_db()

    # Run Rigid
    rigid_session = AgentSession.objects.create(
        agent_type=AgentSession.AgentType.RIGID,
        status=AgentSession.Status.PENDING,
        user_message=message,
        user_name_target=user_name,
    )
    _execute_agent(str(rigid_session.id))
    rigid_session.refresh_from_db()

    # Determine winner
    react_ok = react_session.status == AgentSession.Status.COMPLETED
    rigid_ok = rigid_session.status == AgentSession.Status.COMPLETED

    if react_ok and not rigid_ok:
        winner = "react"
        analysis = "ReAct succeeded where Rigid failed (likely due to ambiguity handling)."
    elif rigid_ok and not react_ok:
        winner = "rigid"
        analysis = "Rigid succeeded where ReAct failed."
    elif react_ok and rigid_ok:
        react_time = react_session.execution_time_ms or 0
        rigid_time = rigid_session.execution_time_ms or 0
        winner = "react" if react_time <= rigid_time else "rigid"
        analysis = (
            f"Both succeeded. ReAct: {react_time}ms, Rigid: {rigid_time}ms. "
            f"{'ReAct' if winner == 'react' else 'Rigid'} was faster."
        )
    else:
        winner = "none"
        analysis = "Both agents failed."

    comparison = AgentComparison.objects.create(
        query=message,
        react_session=react_session,
        rigid_session=rigid_session,
        winner=winner,
        analysis=analysis,
    )

    return comparison


def _execute_recursive_qa(session_id: str, max_refinements: int = 3, target_confidence: float = 0.85):
    """Execute recursive Q&A."""
    from agents.models import AgentSession, AgentStep, QueryHistory
    from agents.services.recursive_qa import RecursiveQAService

    session = AgentSession.objects.get(id=session_id)
    session.status = AgentSession.Status.RUNNING
    session.save(update_fields=["status"])

    _send_ws_update(session_id, {"status": "running", "agent_type": "recursive"})

    try:
        service = RecursiveQAService()
        result = service.run(
            session.user_message,
            max_refinements=max_refinements,
            target_confidence=target_confidence,
        )

        session.status = AgentSession.Status.COMPLETED
        session.final_result = result.get("result")
        session.execution_time_ms = result.get("execution_time_ms")
        session.graph_definition = {"mermaid": service.get_mermaid_definition()}

        # Save refinement history
        for entry in result.get("result", {}).get("refinement_history", []):
            QueryHistory.objects.create(
                session=session,
                iteration=entry.get("iteration", 0),
                original_query=session.user_message,
                refined_query=entry.get("query", ""),
                answer=entry.get("answer", ""),
                confidence_score=entry.get("confidence"),
                is_final=entry.get("is_satisfactory", False),
            )

        # Save steps
        for i, step in enumerate(result.get("step_history", [])):
            AgentStep.objects.create(
                session=session,
                node_name=step.get("node", "unknown"),
                step_number=i + 1,
                status=AgentStep.StepStatus.COMPLETED,
                input_state={"action": step.get("action")},
                output_state=step,
            )

        session.save()
        _send_ws_update(session_id, {
            "status": "completed",
            "result": result.get("result"),
        })

    except Exception as e:
        logger.exception(f"Recursive QA failed: {e}")
        session.status = AgentSession.Status.FAILED
        session.error_message = str(e)
        session.save()
        _send_ws_update(session_id, {"status": "failed", "error": str(e)})


@shared_task(bind=True, queue="agents", max_retries=2)
def run_agent_task(self, session_id: str):
    _execute_agent(session_id)


@shared_task(bind=True, queue="agents")
def run_comparison_task(self, message: str, user_name: str = ""):
    _execute_comparison(message, user_name)


@shared_task(bind=True, queue="agents")
def run_recursive_qa_task(self, session_id: str, max_refinements: int = 3, target_confidence: float = 0.85):
    _execute_recursive_qa(session_id, max_refinements, target_confidence)
