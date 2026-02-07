"""
Recursive Q&A Tuneup Service.

Implements iterative query refinement:
1. Receive initial query
2. Generate answer with confidence score
3. If confidence below threshold, refine query and retry
4. Track all iterations for transparency
5. Use document context when available
"""

import time
import logging
from typing import TypedDict, Optional, List
from datetime import datetime

from django.conf import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class QAEvaluation(BaseModel):
    """Structured output for answer quality evaluation."""
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    is_satisfactory: bool = Field(description="Whether the answer meets quality threshold")
    suggested_refinement: str = Field(description="How to refine the query for better results")
    reasoning: str = Field(description="Why this confidence score was given")


class RecursiveQAState(TypedDict):
    original_query: str
    current_query: str
    current_answer: str
    confidence: float
    target_confidence: float
    iteration: int
    max_iterations: int
    history: list
    document_context: str
    logs: list
    step_history: list
    is_complete: bool


class RecursiveQAService:
    """Recursive Q&A with iterative query refinement and confidence tracking."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )
        self.evaluator = self.llm.with_structured_output(QAEvaluation)
        self._graph = None

    def _log(self, level: str, message: str, state: RecursiveQAState) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        state["logs"].append({"level": level, "time": ts, "message": message})

    def _answer_node(self, state: RecursiveQAState) -> dict:
        """Generate an answer for the current query."""
        iteration = state["iteration"] + 1
        self._log("INFO", f"answer_node: Iteration {iteration} - Answering query", state)

        context_section = ""
        if state.get("document_context"):
            context_section = f"\n\nDocument Context:\n{state['document_context']}"

        history_section = ""
        if state["history"]:
            prev = state["history"][-1]
            history_section = f"""

Previous attempt:
- Query: {prev.get('query', '')}
- Answer: {prev.get('answer', '')}
- Feedback: {prev.get('refinement_suggestion', '')}

Improve upon the previous answer using the feedback above."""

        prompt = f"""Answer the following query thoroughly and accurately.{context_section}{history_section}

Query: {state['current_query']}

Provide a comprehensive, well-structured answer:"""

        answer = self.llm.invoke(prompt).content

        state["step_history"].append({
            "node": "answer_node",
            "action": "answer_generated",
            "iteration": iteration,
            "query": state["current_query"],
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "current_answer": answer,
            "iteration": iteration,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _evaluate_node(self, state: RecursiveQAState) -> dict:
        """Evaluate answer quality and decide whether to refine."""
        self._log("INFO", f"evaluate_node: Evaluating answer quality (iter {state['iteration']})", state)

        prompt = f"""Evaluate the quality of this answer.

Original Query: {state['original_query']}
Current Query: {state['current_query']}
Answer: {state['current_answer']}

Rate the confidence (0-1) based on:
- Completeness: Does it fully address the query?
- Accuracy: Is the information correct and well-supported?
- Clarity: Is the answer clear and well-structured?
- Relevance: Does it directly address what was asked?

If confidence is below {state['target_confidence']}, suggest how to refine the query."""

        evaluation = self.evaluator.invoke(prompt)

        history_entry = {
            "iteration": state["iteration"],
            "query": state["current_query"],
            "answer": state["current_answer"],
            "confidence": evaluation.confidence,
            "is_satisfactory": evaluation.is_satisfactory,
            "refinement_suggestion": evaluation.suggested_refinement,
            "reasoning": evaluation.reasoning,
        }
        new_history = state["history"] + [history_entry]

        should_stop = (
            evaluation.confidence >= state["target_confidence"]
            or state["iteration"] >= state["max_iterations"]
            or evaluation.is_satisfactory
        )

        state["step_history"].append({
            "node": "evaluate_node",
            "action": "evaluation_complete",
            "confidence": evaluation.confidence,
            "is_satisfactory": evaluation.is_satisfactory,
            "should_stop": should_stop,
            "timestamp": datetime.now().isoformat(),
        })

        self._log(
            "INFO",
            f"evaluate_node: confidence={evaluation.confidence:.2f}, "
            f"satisfactory={evaluation.is_satisfactory}, stop={should_stop}",
            state,
        )

        return {
            "confidence": evaluation.confidence,
            "history": new_history,
            "is_complete": should_stop,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _refine_node(self, state: RecursiveQAState) -> dict:
        """Refine the query based on evaluation feedback."""
        self._log("INFO", "refine_node: Refining query based on feedback", state)

        last_eval = state["history"][-1] if state["history"] else {}
        suggestion = last_eval.get("refinement_suggestion", "")

        prompt = f"""Refine this query to get a better answer.

Original Query: {state['original_query']}
Current Query: {state['current_query']}
Previous Answer Quality Issue: {suggestion}

Create a more specific, targeted query that addresses the quality issues.
Return ONLY the refined query text, nothing else."""

        refined = self.llm.invoke(prompt).content.strip()

        state["step_history"].append({
            "node": "refine_node",
            "action": "query_refined",
            "original": state["current_query"],
            "refined": refined,
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "current_query": refined,
            "logs": state["logs"],
            "step_history": state["step_history"],
        }

    def _should_continue(self, state: RecursiveQAState) -> str:
        if state.get("is_complete"):
            return "end"
        return "refine"

    def build_graph(self) -> StateGraph:
        workflow = StateGraph(RecursiveQAState)

        workflow.add_node("answer", self._answer_node)
        workflow.add_node("evaluate", self._evaluate_node)
        workflow.add_node("refine", self._refine_node)

        workflow.add_edge(START, "answer")
        workflow.add_edge("answer", "evaluate")
        workflow.add_conditional_edges(
            "evaluate",
            self._should_continue,
            {"refine": "refine", "end": END},
        )
        workflow.add_edge("refine", "answer")

        return workflow

    def get_compiled_graph(self):
        if self._graph is None:
            self._graph = self.build_graph().compile()
        return self._graph

    def run(
        self,
        query: str,
        document_context: str = "",
        max_refinements: int = 3,
        target_confidence: float = 0.85,
    ) -> dict:
        start = time.time()
        graph = self.get_compiled_graph()

        initial_state: RecursiveQAState = {
            "original_query": query,
            "current_query": query,
            "current_answer": "",
            "confidence": 0.0,
            "target_confidence": target_confidence,
            "iteration": 0,
            "max_iterations": max_refinements,
            "history": [],
            "document_context": document_context,
            "logs": [],
            "step_history": [],
            "is_complete": False,
        }

        output = graph.invoke(initial_state)
        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "status": "completed",
            "result": {
                "final_answer": output.get("current_answer"),
                "final_confidence": output.get("confidence"),
                "total_iterations": output.get("iteration"),
                "refinement_history": output.get("history", []),
            },
            "logs": output.get("logs", []),
            "step_history": output.get("step_history", []),
            "execution_time_ms": elapsed_ms,
        }

    def get_mermaid_definition(self) -> str:
        return """graph TD
    START((Start)) --> answer[Answer Node<br/>Generate Answer]
    answer --> evaluate[Evaluate Node<br/>Quality Assessment]
    evaluate -->|refine| refine[Refine Node<br/>Query Optimization]
    evaluate -->|end| END_NODE((End))
    refine --> answer

    style answer fill:#4CAF50,color:#fff
    style evaluate fill:#FF9800,color:#fff
    style refine fill:#2196F3,color:#fff
    style START fill:#9C27B0,color:#fff
    style END_NODE fill:#f44336,color:#fff"""
